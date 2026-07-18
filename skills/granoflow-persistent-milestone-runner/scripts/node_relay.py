from __future__ import annotations

import re
from enum import Enum
from typing import Any


class ExecutionMode(str, Enum):
    INTERACTIVE = "interactive"
    UNATTENDED = "unattended"
    LAYERED_HANDOFF = "layered_handoff"


class ContractVersion(str, Enum):
    LEGACY_V1 = "legacy_v1"
    BATCH_V2 = "batch_v2"


class NodeLane(str, Enum):
    ANALYSIS = "analysis"
    PLAN = "plan"
    DEV = "dev"
    TEST = "test"
    INTEGRATION = "integration"
    USER = "user"
    CONFIRM = "confirm"
    ACTION = "action"


class ParsedNodeTitle(tuple):
    __slots__ = ()

    def __new__(cls, lane: NodeLane, label: str) -> ParsedNodeTitle:
        return super().__new__(cls, (lane, label))

    @property
    def lane(self) -> NodeLane:
        return self[0]

    @property
    def label(self) -> str:
        return self[1]


_PREFIX = re.compile(r"^\s*\[([a-z]+)]\s*(.+?)\s*$", re.IGNORECASE)


def parse_node_title(
    title: str,
    contract_version: ContractVersion = ContractVersion.LEGACY_V1,
) -> ParsedNodeTitle | None:
    match = _PREFIX.fullmatch(title)
    if match is None:
        return None
    raw_lane = match.group(1).lower()
    try:
        lane = NodeLane(raw_lane)
    except ValueError:
        return None
    if contract_version is ContractVersion.LEGACY_V1 and lane in {
        NodeLane.ANALYSIS,
        NodeLane.INTEGRATION,
        NodeLane.USER,
    }:
        return None
    if contract_version is ContractVersion.BATCH_V2 and lane is NodeLane.CONFIRM:
        return None
    return ParsedNodeTitle(lane, match.group(2))


def eligible_node(
    nodes: list[dict[str, Any]],
    mode: ExecutionMode,
    lanes: set[NodeLane],
    contract_version: ContractVersion = ContractVersion.LEGACY_V1,
) -> dict[str, Any] | None:
    prior_satisfied = True
    for node in nodes:
        if node.get("status") == "deleted":
            continue
        parsed = parse_node_title(str(node.get("title") or ""), contract_version)
        if node.get("status") == "finished":
            continue
        if parsed is None:
            return None
        if (
            contract_version is ContractVersion.LEGACY_V1
            and mode is ExecutionMode.UNATTENDED
            and parsed.lane is NodeLane.CONFIRM
        ):
            continue
        if parsed.lane in {NodeLane.ACTION, NodeLane.USER}:
            return None
        if not prior_satisfied:
            return None
        return node if parsed.lane in lanes else None
    return None


def skippable_confirmations(
    nodes: list[dict[str, Any]],
    contract_version: ContractVersion = ContractVersion.LEGACY_V1,
) -> list[dict[str, Any]]:
    if contract_version is not ContractVersion.LEGACY_V1:
        return []
    result: list[dict[str, Any]] = []
    for node in nodes:
        if node.get("status") in {"finished", "deleted"}:
            continue
        parsed = parse_node_title(str(node.get("title") or ""))
        if parsed is None or parsed.lane is not NodeLane.CONFIRM:
            break
        result.append(node)
    return result
