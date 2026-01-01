# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "anywidget==0.9.21",
#     "mdanalysis==2.10.0",
#     "molviewspec==1.8.1",
#     "openai==2.14.0",
# ]
# ///

import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def _():
    from dataclasses import dataclass
    from pathlib import Path
    from typing import Iterable
    import sys
    import marimo as mo

    if '.' not in sys.path:
        sys.path.insert(0, '.')

    from molstar_widget import MolStarWidget
    return MolStarWidget, Path, mo


@app.cell
def _(MolStarWidget, Path, mo):
    import molviewspec as mvs

    pdb_path = Path('testdata/unbinding_trajectory_results_0.trajectory_system.pdb')
    xtc_path = Path('testdata/unbinding_trajectory_results_0.trajectory.xtc')

    builder = mvs.create_builder()

    builder.download(url='my.xtc').parse(format='xtc').coordinates(ref = 'traj')

    structure = builder.download(url='my.pdb').parse(format='pdb'). \
        model_structure(coordinates_ref='traj')

    structure.component(selector = {'label_comp_id': 'UNK'}). \
        representation(type="ball_and_stick", size_factor=0.7,ignore_hydrogens=True). \
        color(color="blue")

    structure.component(selector = 'all').representation().color(color="white")

    builder.canvas(custom={
        "molstar_postprocessing": {
            "enable_outline": True,
            "enable_shadow": True,
        }})

    widget = MolStarWidget(
        builder=builder,
        data={'my.pdb': pdb_path.read_bytes(),
                   'my.xtc': xtc_path.read_bytes()}
    )

    frame_slider = mo.ui.slider(start=0, stop=99, step=1, value=0, label="Frame index")
    frame_slider
    return frame_slider, mvs, widget


@app.cell
def _(widget):
    widget
    return


@app.cell
def _(frame_slider, widget):
    widget.frame_index = int(frame_slider.value)
    return


@app.cell
def _(MolStarWidget, mvs):
    def create_primitives_example():
        # 1. Create the builder
        builder = mvs.create_builder()

        # 2. Start a "Primitives" group
        # All primitives added to this group share the group's default options 
        # (like opacity) unless overridden individually.
        primitives = builder.primitives(
            opacity=0.8,
            tooltip="Group Tooltip"
        )

        # --- 1. Basic Shapes (Box, Sphere, Ellipsoid) ---

        # Box: defined by center and extent (x, y, z dimensions)
        primitives.box(
            center=(2, 0, 0),
            extent=(1, 1, 1),
            face_color="red",
            tooltip="I am a Box"
        )

        # Sphere: defined by center and radius
        primitives.sphere(
            center=(5, 0, 0),
            radius=1.5,
            color="#0000FF",  # Hex color
            tooltip="I am a Sphere"
        )

        # Ellipsoid: defined by center, orientation axes, and radii
        primitives.ellipsoid(
            center=(10, 0, 0),
            major_axis=(1, 0, 0),  # Direction of major axis
            minor_axis=(0, 1, 0),  # Direction of minor axis
            radius=(1.5, 3.0, 1.0), # Radii along the 3 axes
            color="green",
            tooltip="I am an Ellipsoid"
        )

        # --- 2. Linear Primitives (Line, Tube, Arrow) ---

        # Tube: Cylinder with radius between two points
        primitives.tube(
            start=(0, 8, 0),
            end=(5, 8, 0),
            radius=0.5,
            dash_length=0.2, # Optional: makes the tube dashed
            color="cyan",
            tooltip="Dashed Tube"
        )

        # Arrow: Vector with optional caps
        # You can define it by start/end OR start/direction/length
        primitives.arrow(
            start=(0, 12, 0),
            end=(10, 12, 5),
            tube_radius=0.2,
            show_end_cap=True,
            end_cap_radius=0.6,
            end_cap_length=1.0,
            color="magenta",
            tooltip="Direction Arrow"
        )

        # --- 3. Measurements (Distance, Angle) ---

        primitives.distance(
            start=(0, 0, 0),
            end=(5, 0, 0),
            label_template="Dist: {:.2f} A",
            color="yellow"
        )

        # Angle Measurement: Angle between three points (a-b-c)
        # Visualizes the angle at point b
        primitives.angle(
            a=(5, 0, 0),
            b=(0, 0, 0),  # Vertex
            c=(0, 5, 0),
            label_template="Angle: {:.1f} deg",
            color="white"
        )

        # --- 4. Annotation (Label) ---

        # Floating text label
        primitives.label(
            position=(-2, 1, 1),
            text="Hello Mol*",
            label_size=2,
            label_color="lime",
        )

        return builder

    MolStarWidget(
        builder=create_primitives_example(),
    )
    return


@app.cell
def _(MolStarWidget, mvs):
    def create_selector_example():
        builder = mvs.create_builder()

        selector = [
            # Residue range 50–75 on chain A (label numbering)
            {
                "label_asym_id": "A",
                "beg_label_seq_id": 5,
                "end_label_seq_id": 15
            },

            # Single residue by auth numbering with insertion code
            {
                "auth_asym_id": "A",
                "auth_seq_id": 102,
                #"pdbx_PDB_ins_code": "A"
            },

            # Specific atom name (delta nitrogen carbons only)
            {
                "label_atom_id": "ND2"
            },

            # Specific element (all calcium ions, regardless of location)
            {
                "type_symbol": "CA"
            },

            # Explicit atom by atom_site.id
            {
                "atom_id": 10
            },

            # Explicit atom by 0-based atom index
            {
                "atom_index": 13
            },

            # component id selection
            {
                "label_comp_id": "HIS"
            }
        ]

        structure = builder.download(url='https://files.rcsb.org/download/1TMN.cif').parse(format='mmcif').model_structure()

        structure.component(selector = 'all').representation().color(color="white")

        structure.component(selector = selector). \
            representation(type='ball_and_stick', size_factor=0.4,ignore_hydrogens=False). \
            color(color="blue")

        return builder

    ms =MolStarWidget(
        builder=create_selector_example(),
    )
    ms
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
