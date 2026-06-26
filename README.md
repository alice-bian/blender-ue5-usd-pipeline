# Blender UE5 USD Crowd Pipeline

This repository contains a Blender 5 extension that turns a folder of rigged garment meshes into a USD-based asset library for a crowd diversity pipeline.

## What is included

- Blender extension manifest at [blender_manifest.toml](blender_manifest.toml)
- Add-on package at [crowd_diversity_pipeline](crowd_diversity_pipeline)
- Batch USD export operator with JSON metadata sidecars
- Simple fit-check operator with a few temporary test poses
- A 3D Viewport sidebar panel for category selection, library root, and fit-check actions

## Installation in Blender

1. Open Blender 5.x.
2. Go to Edit > Preferences > Add-ons.
3. Choose Install from Disk and select the repository root folder.
4. Enable the add-on named "Crowd Diversity USD Pipeline".

## Usage

1. Select one or more rigged mesh objects in Blender.
2. Choose an output library root in the add-on preferences or panel.
3. Pick a category and click Export Selected Assets.
4. Use Run Fit Check to inspect temporary poses for clipping before exporting.

## Verification

The core export and metadata logic is covered by the standard-library tests in [tests/test_core.py](tests/test_core.py).
