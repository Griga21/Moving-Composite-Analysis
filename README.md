# Step Analyzer

Step Analyzer is a PyQt-based research tool for inspecting gait videos, coordinate trajectories, and step-cycle signals. The public repository intentionally contains no raw experimental data or videos.

## What Is Included

- GUI application entry point: `app.py`
- Universal Open Field trajectory viewer
- Treadmill angle and magnitude templates
- Input data schemas in `templates/`
- Synthetic example CSV files in `examples/`
- Dependency list in `requirements.txt`

## What Is Not Included

The following are excluded from publication:

- raw experimental CSV files
- video recordings
- generated plots and reports
- IDE settings
- Python cache files
- local virtual environments

## Install

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

On Linux or macOS:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

## Input Format

For Open Field analysis, provide a CSV file with one frame column and any number of coordinate pairs:

```csv
frame,nose_x,nose_y,left_paw_x,left_paw_y,right_paw_x,right_paw_y
0,120,240,150,260,180,262
1,121,241,151,261,181,263
```

The application automatically detects every `*_x` / `*_y` pair and builds plots for each point.

For Treadmill analysis, see:

- `templates/treadmill_angles_template.csv`
- `templates/treadmill_magnitudes_template.csv`
- `templates/metadata_template.csv`

## Example Data

Use `examples/open_field_example.csv` to test trajectory loading without private research data.

## Privacy Note

This repository is prepared for publication without source experimental datasets. Put local data into `data/`, `Trajectory/`, or another ignored directory when running private analyses.
