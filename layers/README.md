# layers/

This directory contains your NFT layer artwork.

## Structure

Create one sub-folder per **layer** (trait category).  The folder names must
match the `"name"` values in `config.json`.

```
layers/
  Background/
    blue.png
    red.png
    ...
  Body/
    circle.png
    square.png
    ...
  Eyes/
    ...
  Accessory/
    ...
```

## Guidelines

* Images should be **PNG** with an **RGBA** (transparent) background so that
  layers composite correctly.
* All layer images are automatically resized to the `width` × `height` set in
  `config.json`, so consistent source sizes produce the sharpest results.
* File names must match the `"file"` values in `config.json` exactly
  (case-sensitive).

## Quick start

Run the sample layer generator to create placeholder images instantly:

```bash
python scripts/create_sample_layers.py
```
