---
name: molstar-integration
description: Integrate Mol* (MolStar) with MolViewSpec into Jupyter notebooks, Marimo notebooks, or custom webapps for visualizing molecules (PDB, SDF, MMCIF, and more) or trajectories (XTC), and for customizing layout and appearance using selectors and primitives.
license: MIT
metadata:
  author: Mikael Hvidtfeldt Christensen
  version: "1.0"
---

# Molstar Integration

## Overview

Integrate Mol* using MolViewSpec (MVSJ/MVSX) across notebooks and webapps. Use the example code in this repo for end-to-end flows and adapt the builder patterns for selectors and primitives.

## Quick Start

1. Use the MolViewSpec builder (via the Python `molviewspec` package) to describe structures (local files or external references) and representations (ball-and-stick, surfaces, coloring, labels).
2. For notebooks (Jupyter and Marimo), pass the builder to `MolStarWidget` together with local data (molecules/trajectories) in a `data` dict.
3. For web apps, use the example below: build an MVSJ description, package it into an MVSX (zip with `index.mvsj` + bundled files), and load it via Mol* `viewer.loadMvsData(bytes, "mvsx")`.

## Concrete implementations

Always start by reading more about the specific type of integration:

- **Jupyter**: `.codex/skills/molstar-integration/references/jupyter.md`
- **Marimo**: `.codex/skills/molstar-integration/references/marimo.md`
- **Webapp**: `.codex/skills/molstar-integration/references/webapp.md`

## Bundled Widget Source

The full AnyWidget wrapper is bundled here for reuse (can be copied directly):

- `.codex/skills/molstar-integration/assets/molstar_widget/`

Complete examples from this repo are bundled as assets:

- `.codex/skills/molstar-integration/assets/notebooks/`
- `.codex/skills/molstar-integration/assets/webapp/`

## MolViewSpec Selectors and Primitives

Use selectors and primitives via the MolViewSpec builder. See:

- `.codex/skills/molstar-integration/references/selectors-primitives.md`

## Representations and Coloring

Use representation parameters and Mol* color themes:

- `.codex/skills/molstar-integration/references/representations-coloring.md`
  - Includes postprocessing examples (outline, shadow, SSAO, fog, background).

## Official Documentation

Reference the official MolViewSpec docs for schema details and capabilities:

- https://molstar.org/mol-view-spec-docs/
