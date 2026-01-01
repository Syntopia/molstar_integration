# MolViewSpec Selectors and Primitives

Use the Marimo notebook (`notebooks/marimo_molstar_demo.py`) as the source of truth.

## Selectors

Static selector (string) chooses a structure subset by entity type. Supported values:
`"all"`, `"polymer"`, `"protein"`, `"nucleic"`, `"branched"`, `"ligand"`, `"ion"`, `"water"`.

```python
selector = [
    {"label_asym_id": "A", "beg_label_seq_id": 5, "end_label_seq_id": 15},
    {"auth_asym_id": "A", "auth_seq_id": 102},
    {"label_atom_id": "ND2"},
    {"type_symbol": "CA"},
    {"atom_id": 10},
    {"atom_index": 13},
    {"label_comp_id": "HIS"},
]

structure = (
    builder.download(url="https://files.rcsb.org/download/1TMN.cif")
    .parse(format="mmcif")
    .model_structure()
)
structure.component(selector="all").representation().color(color="white")
structure.component(selector=selector).representation(
    type="ball_and_stick", size_factor=0.4, ignore_hydrogens=False
).color(color="blue")
```

## Primitives

```python
primitives = builder.primitives(opacity=0.8, tooltip="Group Tooltip")
primitives.box(center=(2, 0, 0), extent=(1, 1, 1), face_color="red")
primitives.sphere(center=(5, 0, 0), radius=1.5, color="#0000FF")
primitives.ellipsoid(
    center=(10, 0, 0),
    major_axis=(1, 0, 0),
    minor_axis=(0, 1, 0),
    radius=(1.5, 3.0, 1.0),
    color="green",
)
primitives.tube(start=(0, 8, 0), end=(5, 8, 0), radius=0.5, color="cyan")
primitives.arrow(
    start=(0, 12, 0),
    end=(10, 12, 5),
    tube_radius=0.2,
    show_end_cap=True,
    end_cap_radius=0.6,
    end_cap_length=1.0,
    color="magenta",
)
primitives.distance(start=(0, 0, 0), end=(5, 0, 0), label_template="Dist: {:.2f} A")
primitives.angle(a=(5, 0, 0), b=(0, 0, 0), c=(0, 5, 0), label_template="Angle: {:.1f} deg")
primitives.label(position=(-2, 1, 1), text="Hello Mol*", label_size=2, label_color="lime")
```
