# VoxForge 🎤

AI Voice Conversion Studio built on RVC (Retrieval-based Voice Conversion).

## Features

- **Speech Conversion** — Text-to-speech + RVC voice conversion (one-click and multi-step)
- **Model Upload** — Upload your own `.pth` / `.index` RVC voice models
- **Audio Format Converter** — Convert audio files between WAV, MP3, FLAC, OGG, and M4A
- **Settings & Presets** — Save and load UI configuration presets

## Quick Start (Google Colab)

Open `notebooks/VoxForge_Colab.ipynb` in Google Colab and run all cells.

## Local Setup

```bash
uv sync --prerelease if-necessary-or-explicit
uv run src/ultimate_rvc/web/main.py --share
```
