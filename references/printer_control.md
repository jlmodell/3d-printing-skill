# Printer control, slicing and AMS — the Bambu MCP

The `Bambu_Printer` MCP is the live path to the printer, and it **also slices**.
When it is present, this is the primary route from file to print: it removes the
old "no slicer profile exists, so hand back a project 3MF" constraint entirely.

Check with `ListConnectors` before claiming any of this. `scripts/preflight.py`
does not test MCP connectors — it only sees local binaries and Python deps. When
the connector is absent, fall back to `print_prep.md`'s project-3MF path.

Tools appear as `mcp__remote-devices__Bambu_Printer__<name>`; the bare names are
used below.

## The one safety rule

**`bambu_model` is required on every slice/print call.** Take the value from
SKILL.md's "Your setup" block — shipped default `"h2c"`. The tool's own description says using the wrong model can
damage the printer — it drives the machine profile, and a mismatched profile is
exactly the fabricated-profile failure this skill exists to prevent. Never guess
it, never let it default, never copy a model string out of a downloaded 3MF.

## Slicing

| Tool | Use |
| --- | --- |
| `slice_stl` | STL or 3MF → sliced 3MF. The workhorse. |
| `slice_with_template` | Same, but pulls settings from a named saved template. |
| `get_slice_settings` | Read settings out of a template/3MF/profile without slicing. |
| `list_templates` / `save_template` | The local template registry. |

`slice_stl` arguments worth knowing:

- `bambu_model: "h2c"` — required, always.
- `slicer_type: "bambustudio"` — the configured slicer (see Your setup;
  chosen over OrcaSlicer for native H2C support). Pass it explicitly rather
  than taking whatever the server defaults to.
- `nozzle_diameter` — `"0.4"`, both the tool default and the configured
  nozzle. Pass `"0.6"` only when the user says the 0.6 is installed; a wrong
  nozzle silently produces wrong extrusion widths.
- `use_printer_filaments: true` — resolves the filament profile from what is
  actually loaded in the AMS instead of a profile default. Prefer this over
  guessing, and see the AMS section below.
- `arrange: true` and `orient: true` — recommended for raw STL imports.
  `arrange: false` preserves a plate layout you deliberately built.
- `ensure_on_bed: true` — catches models floating above z=0. Cheap insurance on
  anything downloaded.
- `uptodate: true` and `skip_modified_gcodes: true` — for downloaded 3MFs.
  `skip_modified_gcodes` strips custom start/end G-code from someone else's
  profile, which may be unsafe on this printer. Use both on MakerWorld files.
- `allow_mix_temp: true` — required when one plate mixes materials with
  different temperatures (PLA + PETG).
- `repetitions` / `clone_objects` — N copies without duplicating the file.
- `scale`, `rotate`, `rotate_x`, `rotate_y` — transforms applied before slicing.
  **Do not use `scale` on a model with hardware interfaces or magnet holes** —
  it scales everything uniformly, which is the exact failure this skill's
  protected-scaling path exists to prevent. Scale with
  `scripts/smart_scale.py` first, then slice the result.
- `slice_plate` — which plate of a multi-plate project; `0` means all.

### Templates are the good habit

A template captures the settings from a 3MF that printed well. Once a
combination works — PETG at 0.12 with the support gap that finally released —
`save_template` it and use `slice_with_template` from then on. That is the
slicing counterpart to logging the print, and the two together are what make the
second attempt at anything cheap. Log the template name in the print log's
`--fix` field so the record and the settings point at each other.

## Printing

| Tool | Use |
| --- | --- |
| `print_3mf` | Print a 3MF. Auto-slices if it has no G-code. |
| `print_3mf_bambu_network` | Same via the FULU BambuNetwork bridge (cloud or LAN). |
| `start_print` / `start_print_job` | Start a job already on the printer. |
| `upload_file` / `upload_gcode` | Push a file to the printer. |
| `pause_print` / `resume_print` / `cancel_print` | Job control. |
| `skip_objects` | Abandon specific objects mid-print. |
| `list_printer_files` / `delete_printer_file` | Printer-side file management. |

`print_3mf` also takes `bambu_model` (`"h2c"`), plus `bed_type` (default
`textured_plate` — confirm which plate is actually installed), `plate_index`,
and the calibration toggles `bed_leveling` / `flow_calibration` /
`vibration_calibration`, all defaulting true. Leave the calibrations on unless
the user asks otherwise.

**Confirm before starting a print.** Slicing is reversible; a print consumes
filament and hours of machine time. Report what you are about to run — plate,
filament slots, estimated time if known — and get a yes. This is the one place
in the whole skill where asking is not optional.

### Salvaging a partly-failed plate

When one object on a multi-object plate has failed and the rest are still
printing, `list_3mf_plate_objects` on the sliced 3MF gives the object IDs and
`skip_objects` abandons just those. That is the recovery move for the
Pattern C plates in `plate_arrangement.md` — the whole reason multi-object
plates are worth the stringing risk.

## AMS and filament

| Tool | Use |
| --- | --- |
| `get_printer_filaments` | Live AMS inventory: loaded material, color, resolved profile paths, match confidence. |
| `resolve_3mf_ams_slots` | Match a sliced 3MF's filament requirements against live inventory, without printing. |
| `reread_ams_rfid` | Re-scan spool tags when inventory looks stale. |
| `set_ams_drying` | Start/stop a drying cycle (AMS Pro / AMS-HT). |

**This replaces every guess about filament.** The old rule — never read a
profile's display color as the loaded filament — now has a real answer: call
`get_printer_filaments` and read it. Report the tray, material and color you
picked back to the user.

Slot indices are absolute: `0-3` = AMS 0, `4-7` = AMS 1, `8-11` = AMS 2, `128+`
= AMS-HT, `254` = external spool. `print_3mf` takes `ams_slots` (one tray per
used filament, in plate order) — prefer it over the project-level `ams_mapping`.
`auto_match_ams: true` does the matching for you; `resolve_3mf_ams_slots` shows
you what it would pick before you commit.

`set_ams_drying` is directly useful here: wet PETG is the recurring suspect in
`troubleshooting.md`, and the printer can dry it without a separate box. When
the log points at moisture, offer the drying cycle rather than only advising it.

## Monitoring

`get_printer_status` for state and progress. `camera_snapshot` captures a chamber
frame — on the H2C this goes over RTSP and needs `ffmpeg` on PATH, so it can
fail for reasons that have nothing to do with the printer. Pass `save_path` to
write the JPEG to disk and then look at it; a first-layer snapshot is worth more
than any amount of reasoning about whether adhesion is holding.

`clear_hms_errors` clears health-management alerts. Read them before clearing
them — an HMS code is the printer telling you what it noticed.

Also available: `set_light`, `set_fan_speed`, `set_temperature`,
`set_print_speed`, `set_airduct_mode`.

## Mesh helpers

The MCP carries its own mesh operations: `get_stl_info`, `scale_stl`,
`rotate_stl`, `lay_flat`, `center_model`, `extend_stl_base`, `merge_vertices`,
`blender_mcp_edit_model`.

**Prefer this skill's `scripts/` for anything measured.** `mesh_info.py` and
`detect_features.py` report the hardware interfaces and magnet holes that the
MCP's tools know nothing about, and `smart_scale.py` is the only path that
scales a body while holding those interfaces fixed. Use the MCP's helpers for
what they are good at — `lay_flat` and `center_model` before slicing,
`get_stl_info` as a quick second opinion, `merge_vertices` on a mesh that fails
watertightness — and never `scale_stl` on a model with hardware in it.

## Privacy

`bambu_serial`, `bambu_token` and `host` all default from the server's
environment. **Leave them unset.** Passing them explicitly means the values pass
through the conversation, and they are exactly what must never be written into a
file. Use placeholders in any documentation: `<printer-lan-ip>`,
`<printer-serial>`, `<access-code>`.
