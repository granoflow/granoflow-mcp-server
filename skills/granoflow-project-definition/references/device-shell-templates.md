# Device Shell Templates (Canonical Frames)

Use this contract whenever `visual_baseline.applicability: required` and the
project renders device frames in HTML prototypes. It keeps outer frames
consistent across agents and models.

## Mandatory Load (fail closed if skipped)

Before authoring App Shell HTML (Project Definition Round B) or any post-Baseline
task/milestone `ui_prototype` that renders a device frame:

```text
granoflow_bundled_skill_reference(
  skillId: "granoflow-project-definition",
  referenceId: "device-shell-templates"
)
```

Skipping fails closed as `device_shell_unread`.

## Default Policy (when the user does not specify a frame)

Resolve `device_shell_profile_id` from `platform_support_matrix.layout_families`
using registry defaults:

| Layout family       | Default profile             | When user specifies                      |
| ------------------- | --------------------------- | ---------------------------------------- |
| `mobile_portrait`   | `iphone_17_pro_portrait_v1` | Android → `android_phone_portrait_v1`    |
| `desktop_landscape` | `macos_tahoe_window_v1`     | Windows → `windows_11_window_v1`         |
| `tablet_portrait`   | `ipad_pro_11_portrait_v1`   | iPad portrait (explicit tablet support)  |
| `tablet_landscape`  | `ipad_pro_11_landscape_v1`  | iPad landscape (explicit tablet support) |

**Portrait phone default = iPhone 17 Pro. Desktop landscape default = macOS.**
Do not substitute Android or Windows unless the user or platform matrix names
that platform as the frame authority for that layout family.

Record overrides on Project Work:

```yaml
platform_support_matrix:
  layout_families:
    - id: mobile_portrait
      device_shell_profile_id: iphone_17_pro_portrait_v1 # omit → same default
    - id: desktop_landscape
      device_shell_profile_id: macos_tahoe_window_v1
```

User chose Android + Windows instead:

```yaml
- id: mobile_portrait
  device_shell_profile_id: android_phone_portrait_v1
- id: desktop_landscape
  device_shell_profile_id: windows_11_window_v1
```

When multiple platforms share one layout family, pick **one** profile id per
family—the frame preview authority—not one HTML page per platform unless the
matrix requires separate layout-family rows.

## Canonical Assets (do not redraw bezels)

Bundled under `skills/granoflow-project-definition/assets/device-shells/`:

| Profile id                  | Layout family       | Platform | Frame                          | Reference viewport   |
| --------------------------- | ------------------- | -------- | ------------------------------ | -------------------- |
| `iphone_17_pro_portrait_v1` | `mobile_portrait`   | iOS      | iPhone 17 Pro + Dynamic Island | 402 × 874 @ dpr 3    |
| `android_phone_portrait_v1` | `mobile_portrait`   | Android  | Material phone + punch-hole    | 412 × 915 @ dpr 3    |
| `ipad_pro_11_portrait_v1`   | `tablet_portrait`   | iOS      | iPad Pro 11 portrait           | 834 × 1194 @ dpr 2   |
| `ipad_pro_11_landscape_v1`  | `tablet_landscape`  | iOS      | iPad Pro 11 landscape          | 1194 × 834 @ dpr 2   |
| `macos_tahoe_window_v1`     | `desktop_landscape` | macOS    | Tahoe window + traffic lights  | 1280 × 800 @ dpr 2   |
| `windows_11_window_v1`      | `desktop_landscape` | Windows  | Win11 window + caption buttons | 1280 × 800 @ dpr 1.5 |

Registry: `assets/device-shells/device-shell-registry.json`
(`defaults_by_layout_family` holds the default map above).

**Hard rule:** copy CSS + frame fragments verbatim. Style **inside**
`gf-device-shell__content` with locked Spec tokens and App Shell widgets. Do
**not** invent alternate bezels, traffic-light layouts, or viewport sizes for
the same profile id.

## Copy Into Every Prototype Package

At Project Definition (Round B) and before packaging any Baseline or task
prototype.

**Typical phone + desktop project (defaults only):**

```text
python skills/granoflow-project-definition/scripts/copy_device_shell_assets.py \
  --dest <prototype-source-dir> \
  --layout-families mobile_portrait,desktop_landscape
```

**User chose Android phone + Windows desktop:**

```text
python skills/granoflow-project-definition/scripts/copy_device_shell_assets.py \
  --dest <prototype-source-dir> \
  --layout-families mobile_portrait,desktop_landscape \
  --layout-bindings '{"mobile_portrait":"android_phone_portrait_v1","desktop_landscape":"windows_11_window_v1"}'
```

**Project includes iPad:**

```text
python skills/granoflow-project-definition/scripts/copy_device_shell_assets.py \
  --dest <prototype-source-dir> \
  --layout-families mobile_portrait,tablet_portrait,tablet_landscape,desktop_landscape
```

Each profile lands under `<dest>/device-shells/<profile_id>/`.

Link the copied CSS from each layout HTML page:

```html
<link rel="stylesheet" href="device-shells/iphone_17_pro_portrait_v1/device-shell.css" />
```

Insert the matching `frame.html` fragment around App Shell content. Replace
`<!-- APP_SHELL_CONTENT -->` with `app_shell.top_bar`, page surface, and
`app_shell.bottom_navigation`.

Required markers on the outer shell node:

```html
data-device-shell="iphone_17_pro_portrait_v1" data-layout-family="mobile_portrait"
data-product-ui="true"
```

## Platform Matrix Binding

When a layout family uses a canonical shell, record on Project Work:

```yaml
platform_support_matrix:
  layout_families:
    - id: mobile_portrait
      orientation: portrait
      device_shell_profile_id: iphone_17_pro_portrait_v1
      reference_viewport: { width: 402, height: 874, dpr: 3 }
    - id: tablet_portrait
      orientation: portrait
      device_shell_profile_id: ipad_pro_11_portrait_v1
      reference_viewport: { width: 834, height: 1194, dpr: 2 }
    - id: tablet_landscape
      orientation: landscape
      device_shell_profile_id: ipad_pro_11_landscape_v1
      reference_viewport: { width: 1194, height: 834, dpr: 2 }
    - id: desktop_landscape
      orientation: landscape
      device_shell_profile_id: macos_tahoe_window_v1
      reference_viewport: { width: 1280, height: 800, dpr: 2 }
```

`reference_viewport` Must match the profile in the registry for that
`device_shell_profile_id`. Omit `device_shell_profile_id` only when the layout
family has no HTML device frame; otherwise apply registry defaults.

## Lint (hard)

After HTML authoring, validate every layout page:

```text
python skills/granoflow-project-definition/scripts/lint_device_shell.py \
  mobile.html desktop.html \
  --layout-families mobile_portrait,desktop_landscape
```

Pass explicit overrides:

```text
python skills/granoflow-project-definition/scripts/lint_device_shell.py \
  mobile.html \
  --layout-families mobile_portrait \
  --layout-bindings '{"mobile_portrait":"android_phone_portrait_v1"}'
```

Or pass explicit profile ids with `--profiles`.

Set on Task Work / Baseline craft checklist:

```yaml
craft_checklist:
  device_shell_ok: true # only after load + copy + lint ok
```

## Relationship To App Shell

| Layer                             | Owns                                                              |
| --------------------------------- | ----------------------------------------------------------------- |
| **Device shell** (this reference) | Physical frame: phone/tablet bezel or desktop window chrome       |
| **App Shell**                     | In-app top bar + bottom navigation + Spec tokens inside the frame |
| **Task page**                     | Screen content inside App Shell roles                             |

Device shells are **not** navigation chrome. They wrap App Shell. Removing
`app_shell.top_bar` or `app_shell.bottom_navigation` still fails
`shell_top_bar_missing` / `shell_bottom_navigation_missing`.

## Fail-closed Codes

| Code                              | When                                    |
| --------------------------------- | --------------------------------------- |
| `device_shell_unread`             | Reference not loaded via MCP            |
| `device_shell_profile_missing`    | Required `data-device-shell` absent     |
| `device_shell_profile_unknown`    | Unknown profile id in HTML              |
| `device_shell_profile_unexpected` | Extra profile not in matrix             |
| `device_shell_layout_mismatch`    | `data-layout-family` ≠ registry         |
| `device_shell_product_ui_missing` | Missing `data-product-ui="true"`        |
| `device_shell_assets_not_copied`  | Package missing `device-shells/` assets |
| `device_shell_lint_failed`        | Lint script error                       |

Any of the above keeps `device_shell_ok: false` and blocks Baseline confirm or
`visualConfirmed=true` until fixed.

## Admission Test

1. Did we load this reference via MCP?
2. Did we copy bundled assets (not hand-drawn bezels)?
3. Does each required layout HTML declare the correct `data-device-shell`?
4. Is App Shell content inside `gf-device-shell__content` with locked tokens?
5. Would two different models produce the same outer frame geometry?

If any answer is no, revise before confirm.
