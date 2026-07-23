#!/usr/bin/env python3
"""MCP skill orchestrator — read-only audit + recommendations (no writes).

Scans skills/* under the granoflow-mcp-server repo, emits a machine-readable
report and a human Markdown recommendation pack. Never runs skill-polish or
mutates skill files. Apply steps require a separately confirmed plan file.

External polish/validate CLIs under ~/.codex/skills are optional probes only.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCHEMA = "granoflow_mcp_skill_orchestrate_v1"
MAX_DESCRIPTION_LENGTH = 1024
# Soft smell only — mature contracts may be long on purpose.
LONG_SKILL_LINES = 500
DRAFT_PATTERNS = (
    r"\bTODO\b",
    r"\bTBD\b",
    r"\bFIXME\b",
    r"\bWIP\b",
    r"placeholder",
    r"lorem ipsum",
    r"\[\[.*\]\]",
    r"your[_-]skill[_-]name",
)

SECTION_HINTS = (
    ("keyword", re.compile(r"^##\s+Keyword\b", re.I | re.M)),
    ("when_to_use", re.compile(r"^##\s+When to use\b", re.I | re.M)),
    ("workflow", re.compile(r"^##\s+Workflow\b", re.I | re.M)),
    ("success_criteria", re.compile(r"^##\s+Success [Cc]riteria\b", re.I | re.M)),
)


@dataclass
class Finding:
    code: str
    severity: str  # info | warn | error
    message: str
    path: str | None = None


@dataclass
class SkillAudit:
    skill_id: str
    path: str
    ok_structure: bool
    line_count: int
    description_length: int
    findings: list[Finding] = field(default_factory=list)
    recommendation: str = "keep"
    # keep | steward_audit | polish_candidate | manual_review | fix_structure
    rationale: str = ""
    polish_allowed: bool = False
    design_lock_path: str | None = None
    reference_files: list[str] = field(default_factory=list)
    missing_sections: list[str] = field(default_factory=list)
    draft_hits: list[str] = field(default_factory=list)


def repo_root_from_script() -> Path:
    # skills/granoflow-skill-orchestrator/scripts/this.py → repo root
    return Path(__file__).resolve().parents[3]


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    block = text[3:end].strip()
    result: dict[str, str] = {}
    key: str | None = None
    buf: list[str] = []
    for line in block.splitlines():
        if line.startswith("  ") and key == "description":
            buf.append(line.strip())
            continue
        m = re.match(r"^(name|description):\s*(.*)$", line)
        if not m:
            continue
        if key == "description" and buf:
            result["description"] = " ".join(buf).strip()
            buf = []
        key = m.group(1)
        assert key is not None
        value = m.group(2).strip()
        if value in (">-", ">"):
            buf = []
            continue
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        if key == "description" and not value:
            buf = []
            continue
        result[key] = value
        key = None
    if key == "description" and buf:
        result["description"] = " ".join(buf).strip()
    return result


def list_skill_dirs(skills_root: Path) -> list[Path]:
    if not skills_root.is_dir():
        return []
    return sorted(p for p in skills_root.iterdir() if p.is_dir() and (p / "SKILL.md").is_file())


def find_design_lock(repo: Path, skill_id: str) -> Path | None:
    """Look for an optional design lock under temp/ (non-authoritative)."""
    temp = repo / "temp"
    if not temp.is_dir():
        return None
    patterns = (
        f"{skill_id}-design-lock*.json",
        f"{skill_id.removeprefix('granoflow-')}-design-lock*.json",
        f"*{skill_id}*design*lock*.json",
    )
    hits: list[Path] = []
    for pat in patterns:
        hits.extend(temp.glob(pat))
    # Prefer shortest path name
    hits = sorted({h.resolve() for h in hits if h.is_file()}, key=lambda p: len(p.name))
    return hits[0] if hits else None


def audit_skill(repo: Path, skill_dir: Path) -> SkillAudit:
    skill_id = skill_dir.name
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines()
    fm = parse_frontmatter(text)
    findings: list[Finding] = []
    ok = True

    name = fm.get("name", "")
    desc = fm.get("description", "")
    if not name:
        ok = False
        findings.append(
            Finding(
                "frontmatter_name_missing",
                "error",
                "SKILL.md frontmatter missing name",
                str(skill_md),
            )
        )
    elif name != skill_id:
        ok = False
        findings.append(
            Finding(
                "frontmatter_name_mismatch",
                "error",
                f"frontmatter name={name!r} != directory {skill_id!r}",
                str(skill_md),
            )
        )
    if not desc:
        ok = False
        findings.append(
            Finding(
                "frontmatter_description_missing",
                "error",
                "SKILL.md frontmatter missing description",
                str(skill_md),
            )
        )
    elif len(desc) > MAX_DESCRIPTION_LENGTH:
        ok = False
        findings.append(
            Finding(
                "frontmatter_description_too_long",
                "error",
                f"description length {len(desc)} > {MAX_DESCRIPTION_LENGTH}",
                str(skill_md),
            )
        )

    missing_sections: list[str] = []
    for label, rx in SECTION_HINTS:
        if not rx.search(text):
            missing_sections.append(label)
            findings.append(
                Finding(
                    "section_hint_missing",
                    "warn",
                    f"Recommended section not found: {label}",
                    str(skill_md),
                )
            )

    draft_hits: list[str] = []
    for pat in DRAFT_PATTERNS:
        if re.search(pat, text, flags=re.I):
            draft_hits.append(pat)
            findings.append(
                Finding(
                    "draft_smell",
                    "warn",
                    f"Draft-shaped pattern matched: {pat}",
                    str(skill_md),
                )
            )

    refs_dir = skill_dir / "references"
    reference_files: list[str] = []
    if refs_dir.is_dir():
        reference_files = sorted(
            str(p.relative_to(skill_dir)) for p in refs_dir.rglob("*.md") if p.is_file()
        )

    # Broken relative reference links to references/*.md
    for m in re.finditer(r"\]\((references/[^)#\s]+)\)", text):
        rel = m.group(1)
        target = skill_dir / rel
        if not target.is_file():
            ok = False
            findings.append(
                Finding(
                    "broken_reference_link",
                    "error",
                    f"SKILL.md links to missing {rel}",
                    str(skill_md),
                )
            )

    design_lock = find_design_lock(repo, skill_id)
    long_body = len(lines) >= LONG_SKILL_LINES
    if long_body:
        findings.append(
            Finding(
                "skill_md_long",
                "info",
                f"SKILL.md has {len(lines)} lines "
                f"(≥{LONG_SKILL_LINES}); consider references if draft-shaped",
                str(skill_md),
            )
        )

    # Recommendation policy — polish never auto-selected without design lock + draft smell
    polish_allowed = False
    if not ok:
        recommendation = "fix_structure"
        rationale = "Structure errors must be fixed before any polish/validate apply step."
    elif draft_hits and design_lock is not None:
        recommendation = "polish_candidate"
        polish_allowed = True
        rationale = (
            "Draft smells present and a design lock was found under temp/. "
            "Human must confirm before skill-polish; keep Hard Gates intact."
        )
    elif draft_hits:
        recommendation = "manual_review"
        rationale = (
            "Draft smells present but no design lock. Do not polish by guessing; "
            "confirm design or fix smells manually."
        )
    elif missing_sections and long_body:
        recommendation = "manual_review"
        rationale = "Long SKILL.md with missing section hints — human should decide keep vs split."
    elif missing_sections:
        recommendation = "steward_audit"
        rationale = "Minor section-hint gaps; steward 8-point audit is enough (no polish)."
    else:
        recommendation = "keep"
        rationale = (
            "Mature structure; no polish. " "Optional steward_audit only if memory/registry needed."
        )

    return SkillAudit(
        skill_id=skill_id,
        path=str(skill_dir.relative_to(repo)),
        ok_structure=ok,
        line_count=len(lines),
        description_length=len(desc),
        findings=findings,
        recommendation=recommendation,
        rationale=rationale,
        polish_allowed=polish_allowed,
        design_lock_path=str(design_lock.relative_to(repo)) if design_lock else None,
        reference_files=reference_files,
        missing_sections=missing_sections,
        draft_hits=draft_hits,
    )


def probe_external_tooling() -> dict[str, Any]:
    home = Path.home()
    polish = home / ".codex" / "skills" / "skill-polish" / "scripts" / "skill_polish.py"
    validate = home / ".codex" / "skills" / "skill-validate" / "scripts" / "skill_validate.py"
    authoring = home / ".codex" / "skills" / "skill-authoring" / "scripts" / "skill_authoring.py"
    steward = home / ".codex" / "skills" / "skill-steward" / "SKILL.md"
    return {
        "skill_polish": {"path": str(polish), "present": polish.is_file()},
        "skill_validate": {"path": str(validate), "present": validate.is_file()},
        "skill_authoring": {"path": str(authoring), "present": authoring.is_file()},
        "skill_steward": {"path": str(steward), "present": steward.is_file()},
        "note": "External tools are never invoked by this audit. Apply only after human confirm.",
    }


def build_report(repo: Path, audits: list[SkillAudit]) -> dict[str, Any]:
    by_rec: dict[str, list[str]] = {}
    for a in audits:
        by_rec.setdefault(a.recommendation, []).append(a.skill_id)

    recommended_plan = {
        "phase": "report_only",
        "status": "awaiting_human_confirmation",
        "hard_rules": [
            "Do not run skill-polish on mature skills without confirmed design lock.",
            "Do not mutate skills until a confirmed plan file is provided.",
            "Preserve Hard Gates / fail-closed codes; polish must not invent gates.",
            "Default recommendation for healthy skills is keep.",
        ],
        "buckets": by_rec,
        "next_steps_for_human": [
            "Review temp Markdown/JSON report.",
            "Approve or edit the recommendation buckets.",
            "Only then ask the agent to execute a confirmed apply plan (future --apply-plan).",
        ],
    }

    return {
        "schema": SCHEMA,
        "generated_at": datetime.now(UTC).isoformat(),
        "repo": str(repo),
        "mode": "audit_report",
        "skill_count": len(audits),
        "external_tooling": probe_external_tooling(),
        "summary": {
            "ok_structure": sum(1 for a in audits if a.ok_structure),
            "structure_errors": sum(1 for a in audits if not a.ok_structure),
            "by_recommendation": {k: len(v) for k, v in sorted(by_rec.items())},
            "polish_candidates": by_rec.get("polish_candidate", []),
        },
        "recommended_plan": recommended_plan,
        "skills": [
            {
                **{k: v for k, v in asdict(a).items() if k != "findings"},
                "findings": [asdict(f) for f in a.findings],
            }
            for a in audits
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = [
        "# MCP Skill Orchestrate Report",
        "",
        f"- Generated: `{report['generated_at']}`",
        f"- Mode: `{report['mode']}` (read-only; awaiting human confirmation)",
        f"- Skills scanned: **{report['skill_count']}**",
        f"- Structure OK: **{report['summary']['ok_structure']}** / errors: "
        f"**{report['summary']['structure_errors']}**",
        "",
        "## Recommendation buckets",
        "",
    ]
    buckets = report["recommended_plan"]["buckets"]
    for key in sorted(buckets):
        ids = buckets[key]
        lines.append(f"### `{key}` ({len(ids)})")
        lines.append("")
        for sid in ids:
            lines.append(f"- `{sid}`")
        lines.append("")

    lines.extend(
        [
            "## Hard rules",
            "",
        ]
    )
    for rule in report["recommended_plan"]["hard_rules"]:
        lines.append(f"- {rule}")
    lines.extend(["", "## Per-skill rationale", ""])
    for skill in report["skills"]:
        lines.append(f"### `{skill['skill_id']}` → `{skill['recommendation']}`")
        lines.append("")
        lines.append(f"- Path: `{skill['path']}`")
        lines.append(
            f"- Lines: {skill['line_count']}; " f"description chars: {skill['description_length']}"
        )
        lines.append(f"- Polish allowed (gated): `{skill['polish_allowed']}`")
        if skill.get("design_lock_path"):
            lines.append(f"- Design lock: `{skill['design_lock_path']}`")
        lines.append(f"- Rationale: {skill['rationale']}")
        errors = [f for f in skill["findings"] if f["severity"] == "error"]
        warns = [f for f in skill["findings"] if f["severity"] == "warn"]
        if errors:
            lines.append(f"- Errors ({len(errors)}): " + "; ".join(e["code"] for e in errors[:8]))
        if warns:
            lines.append(f"- Warns ({len(warns)}): " + "; ".join(w["code"] for w in warns[:8]))
        lines.append("")

    lines.extend(
        [
            "## Next steps (human)",
            "",
        ]
    )
    for i, step in enumerate(report["recommended_plan"]["next_steps_for_human"], 1):
        lines.append(f"{i}. {step}")
    lines.append("")
    lines.append(
        "After confirmation, provide an approved plan (or say which buckets to execute). "
        "This tool will not polish or rewrite until then."
    )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MCP skill orchestrator (audit/report only)")
    parser.add_argument(
        "--repo",
        type=Path,
        default=None,
        help="Repository root (default: detect from script location)",
    )
    parser.add_argument(
        "--skills-dir",
        type=Path,
        default=None,
        help="Skills directory (default: <repo>/skills)",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Write JSON report path (default: <repo>/temp/mcp-skill-orchestrate-report.json)",
    )
    parser.add_argument(
        "--md-out",
        type=Path,
        default=None,
        help="Write Markdown report path (default: <repo>/temp/mcp-skill-orchestrate-report.md)",
    )
    parser.add_argument(
        "--skill",
        action="append",
        default=[],
        help="Limit to one or more skill directory names (repeatable)",
    )
    parser.add_argument(
        "--apply-plan",
        type=Path,
        default=None,
        help=(
            "Confirmed plan JSON (refused unless status=confirmed); " "mutate not implemented yet"
        ),
    )
    args = parser.parse_args(argv)

    repo = (args.repo or repo_root_from_script()).resolve()
    skills_root = (args.skills_dir or (repo / "skills")).resolve()

    if args.apply_plan is not None:
        plan_path = args.apply_plan.resolve()
        if not plan_path.is_file():
            print(json.dumps({"ok": False, "code": "apply_plan_missing", "path": str(plan_path)}))
            return 2
        try:
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(json.dumps({"ok": False, "code": "apply_plan_invalid_json", "error": str(exc)}))
            return 2
        if plan.get("status") != "confirmed":
            print(
                json.dumps(
                    {
                        "ok": False,
                        "code": "apply_plan_unconfirmed",
                        "message": (
                            "Refusing apply: plan.status must be " "'confirmed' after human review."
                        ),
                    }
                )
            )
            return 3
        print(
            json.dumps(
                {
                    "ok": False,
                    "code": "apply_not_implemented",
                    "message": (
                        "Apply phase is intentionally not implemented in this release. "
                        "Use the report recommendations; have the agent execute confirmed "
                        "edits skill-by-skill after human approval."
                    ),
                }
            )
        )
        return 4

    dirs = list_skill_dirs(skills_root)
    if args.skill:
        wanted = set(args.skill)
        dirs = [d for d in dirs if d.name in wanted]
        missing = wanted - {d.name for d in dirs}
        if missing:
            print(json.dumps({"ok": False, "code": "skill_not_found", "missing": sorted(missing)}))
            return 2

    audits = [audit_skill(repo, d) for d in dirs]
    report = build_report(repo, audits)
    md = render_markdown(report)

    temp = repo / "temp"
    temp.mkdir(parents=True, exist_ok=True)
    json_out = (args.json_out or (temp / "mcp-skill-orchestrate-report.json")).resolve()
    md_out = (args.md_out or (temp / "mcp-skill-orchestrate-report.md")).resolve()
    json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_out.write_text(md, encoding="utf-8")

    print(
        json.dumps(
            {
                "ok": True,
                "code": "ok",
                "schema": SCHEMA,
                "json_out": str(json_out),
                "md_out": str(md_out),
                "summary": report["summary"],
                "awaiting_human_confirmation": True,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
