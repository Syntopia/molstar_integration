# Marimo Integration (MolViewSpec)

Use `notebooks/marimo_molstar_demo.py` as the canonical example. Key parts:

```python
import marimo as mo
import molviewspec as mvs
from pathlib import Path
from molstar_widget import MolStarWidget

pdb_path = Path("my_local_protein.pdb")
xtc_path = Path("my_local_trajectory.xtc")

builder = mvs.create_builder()
builder.download(url="my.xtc").parse(format="xtc").coordinates(ref="traj")
structure = (
    builder.download(url="my.pdb")
    .parse(format="pdb")
    .model_structure(coordinates_ref="traj")
)

structure.component(selector={"label_comp_id": "UNK"}).representation(
    type="ball_and_stick", size_factor=0.7, ignore_hydrogens=True
).color(color="blue")
structure.component(selector="all").representation().color(color="white")

widget = MolStarWidget(
    builder=builder,
    data={"my.pdb": pdb_path.read_bytes(), "my.xtc": xtc_path.read_bytes()},
)

frame_slider = mo.ui.slider(start=0, stop=99, step=1, value=0, label="Frame index")
widget.frame_index = int(frame_slider.value)

frame_slider
widget
```

Notes:
- Do not put logic and code for setting up and preparing state into separate files. Put it in the Marimo notebook, unless otherwise asked for.
- Put all imports and code inside `@app.cell` functions (no global imports or functions outside @app.cell!).
- Underscore-prefixed variables are cell-local and not visible to later cells. Most widget definations should be global (no underscore).
- You cannot refer to a widgets state in the same cell that created it.
- Ensure `frame_index` is updated in its own cell (avoid UI element state dependence in the same cell).
- Put imports in the first `@app.cell` and add the local module path, for example:

```python
@app.cell
def _():
    import sys
    import marimo as mo

    if '.' not in sys.path:
        sys.path.insert(0, '.')

    from molstar_widget import MolStarWidget
    return MolStarWidget, mo
```
