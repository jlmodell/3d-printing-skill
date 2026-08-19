# Finding models on MakerWorld

Use when the user wants an existing model rather than a designed one —
especially for organic or sculpted shapes, which the parametric paths in this
skill are not suited for.

## Requirements

Browsing needs a live browser automation path (the `claude-in-chrome` skill /
`mcp__claude-in-chrome__*` tools, or an equivalent agent-browser). Check it is
available before promising to go look. If it is not, hand the user a search URL
and let them pick.

## Workflow

1. Navigate to `https://makerworld.com/en/search/models?keyword={query}`.
2. Screenshot the results and present options with thumbnails. **Always show
   the user the model before downloading it** — thumbnails are how they judge
   fit, and a wrong download wastes a print.
3. User picks one → navigate to the model page.
4. Check whether the model posts a source 3MF as well as STLs. A source 3MF
   often carries the designer's own profile, paint and plate layout, and saves
   substantial work. Prefer it when remixing.
5. Click "Download raw model files" for STL/STEP, or take the source 3MF.
6. Save into a working directory (e.g. `/tmp/makerworld/`), not `~/Downloads`.
7. Inspect with `scripts/mesh_info.py` before doing anything else — downloaded
   meshes are frequently non-watertight, mis-scaled, or in inches.

## Notes

- Login may be required for downloads. Use only an existing authenticated
  browser session, or a flow the user explicitly approves. Never ask the user
  to paste credentials into chat, and never store them in a file.
- MakerWorld has bot detection. Browse at a realistic pace; do not hammer.
- Check the licence before remixing and redistributing. Personal printing is
  usually fine; publishing a remix may not be.

## Remixing

The mesh is the ground truth. When a downloaded model mates with hardware —
magnets, bearings, movements — measure the holes with
`scripts/detect_features.py` and preserve the *measured* clearance the designer
chose, rather than substituting a nominal catalog value. See the protected
scaling section of SKILL.md.
