# Webapp Integration (FastAPI + MolViewSpec)

Use the `webapp/` folder in this repo as the example:

- `webapp/app.py`: FastAPI backend that scans `testdata/` for trajectory pairs and serves MVSX.
- `webapp/static/app.js`: Mol* viewer setup and frame slider updates.
- `webapp/templates/index.html`: UI with dropdown + slider.

Minimal flow (server):

```python
builder = mvs.create_builder()
builder.download(url="trajectory.xtc").parse(format="xtc").coordinates(ref="traj")
structure = (
    builder.download(url="trajectory.pdb")
    .parse(format="pdb")
    .model_structure(coordinates_ref="traj")
)
structure.component(selector={"label_comp_id": "UNK"}).representation(
    type="ball_and_stick", size_factor=0.7, ignore_hydrogens=True
).color(color="blue")
structure.component(selector="all").representation().color(color="white")

with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
    archive.writestr("index.mvsj", builder.get_state().model_dump_json(exclude_none=True, indent=2))
    archive.writestr("trajectory.pdb", pdb_path.read_bytes())
    archive.writestr("trajectory.xtc", xtc_path.read_bytes())
```

Minimal flow (client):

```js
await viewer.loadMvsData(bytes, "mvsx");
await updateModelIndex(viewer.plugin, Number(slider.value));
```

Notes:
- Keep Mol* layout defaults aligned with the widget (controls off, log on, no welcome).
- Use dynamic lookup for `modelIndex`/`frameIndex` updates to avoid stale refs.
- Start with "viewportShowExpand: false" to avoid going fullscreen.
