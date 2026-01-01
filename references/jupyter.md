# Jupyter Integration (MolViewSpec)

Use `notebooks/jupyter_molstar_demo.ipynb` as the canonical example. Key parts:

```python
from pathlib import Path
import ipywidgets as widgets
from IPython.display import display
import molviewspec as mvs
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

frame_slider = widgets.IntSlider(value=0, min=0, max=99, step=1, description="Frame index")
widgets.jslink((frame_slider, "value"), (widget, "frame_index"))
display(frame_slider, widget)
```

Notes:
- Use `widgets.jslink` to drive `frame_index` without extra callbacks.
- The widget expects MolViewSpec MVSX (zip with `index.mvsj` + bundled files).
