# Representations and Coloring

## representation

Creates a visual representation of a component. Parent: `component`, `component_from_uri`, or `component_from_source`.

Supported `type` values:
`cartoon`, `backbone`, `ball_and_stick`, `line`, `spacefill`, `carbohydrate`, `surface`.

Params by type:

- `cartoon`
  - `size_factor` (number, default 1): scales visuals.
  - `tubular_helices` (bool, default false): simplify helices to tubes.
- `backbone`
  - `size_factor` (number, default 1)
- `ball_and_stick`
  - `size_factor` (number, default 1)
  - `ignore_hydrogens` (bool, default false)
- `line`
  - `size_factor` (number, default 1)
  - `ignore_hydrogens` (bool, default false)
- `spacefill`
  - `size_factor` (number, default 1)
  - `ignore_hydrogens` (bool, default false)
- `carbohydrate`
  - `size_factor` (number, default 1)
- `surface`
  - `surface_type` ("molecular" | "gaussian", default "molecular")
  - `size_factor` (number, default 1)
  - `ignore_hydrogens` (bool, default false)

## coloring

Apply a solid color:

```python
structure.component(selector="all").representation().color(color="red")
structure.component(selector="all").representation().color(color="#FF0011")
```

### Custom Mol* theme coloring

```python
structure.component(selector="all").representation().color(
    custom={"molstar_color_theme_name": "sequence-id"}
)
```

`molstar_color_theme_name` accepts any string registered in the Mol* theme registry. Common values:

Standard element & chemical coloring:
- `element-symbol`
- `element-index`
- `carbohydrate-symbol`

Chain & entity coloring:
- `chain-id`
- `entity-id`
- `molecule-type`

Polymer & residue properties:
- `polymer-index`
- `sequence-id`
- `residue-name`
- `secondary-structure`
- `hydrophobicity`

Other useful themes:
- `occupancy`
- `uncertainty`
- `uniform`
- `illustrative`

## Postprocessing (canvas)

Example canvas postprocessing payload (outline, shadow, SSAO, fog, background):

```python
builder.canvas(custom={
    "molstar_postprocessing": {
        # 1. OUTLINE (See mol-canvas3d/passes/outline.ts)
        "enable_outline": True,
        "outline_params": {
            "scale": 1.0,       # Thickness of the outline
            "threshold": 0.33,  # Edge detection sensitivity
            "color": 0x000000,  # Black outline
            "includeTransparent": True
        },

        # 2. SHADOW (See mol-canvas3d/passes/shadow.ts)
        "enable_shadow": True,
        "shadow_params": {
            "bias": 0.003,       # Offset to reduce self-shadowing artifacts
            "maxDistance": 60.0, # (Often "Projection Radius") Max distance for shadow casting
            "steps": 4,          # Quality of the shadow smoothing
            "tolerance": 1.0     # Error tolerance for the shadow map
        },

        # 3. OCCLUSION / SSAO (See mol-canvas3d/passes/occlusion.ts)
        "enable_ssao": True, 
        "ssao_params": {
            "samples": 32,       # Number of samples (higher = smoother but slower)
        },

        # 4. FOG (See mol-canvas3d/passes/fog.ts)
        "enable_fog": True,
        "fog_params": {
            "intensity": 80.0
        },

        # 5. BACKGROUND (See mol-canvas3d/passes/background.ts)
        "background": {
            "name": "horizontalGradient", # options: "solid", "horizontalGradient", "radialGradient"
            "params": {
                "topColor": 0xDDDDDD,    # Light gray top
                "bottomColor": 0xFFFFFF  # White bottom
            }
        }
    }
})
```
