# Input Data Schema

This project should keep raw experimental data outside git. Store real CSV/video files in `data/`, `Trajectory/`, or another local folder ignored by `.gitignore`. Commit only templates, processing code, and documentation.

## 1. Experiment Metadata

File example: `templates/metadata_template.csv`

Required columns:

- `Group`: experimental group, for example `Intact`, `SCI`, `SCI_TMT`.
- `Day`: day after injury or experiment day. Use `0` or `1` for intact baseline consistently.
- `Number Rat`: animal id inside the group.
- `Name video`: source video filename.
- `Step Distance`: minimum distance between step cycle points, in frames.
- `Angle Distance`: minimum angular amplitude for step detection.

## 2. Treadmill Angle Data

File naming:

- `Intact_1_angles.csv`
- `SCI_7_dpi_3_angles.csv`
- `SCI_TMT_14_dpi_5_angles.csv`

Required columns:

- `elbow_collarbone_paw`
- `hip_iliac_crest_knee`
- `knee_hip_ankle`
- `ankle_knee_mtp`

Each row is one video frame. Empty or invalid values may be stored as `NaN`.

## 3. Treadmill Segment Length Data

File naming mirrors angle data:

- `Intact_1_magnitudes.csv`
- `SCI_7_dpi_3_magnitudes.csv`

Required columns:

- `elbow_collarbone_magnitude`
- `elbow_paw_magnitude`
- `hip_iliac_crest_magnitude`
- `hip_knee_magnitude`
- `knee_hip_magnitude`
- `knee_ankle_magnitude`
- `ankle_knee_magnitude`
- `ankle_mtp_magnitude`

## 4. Open Field Trajectory Data

File example: `templates/open_field_trajectory_template.csv`

Required columns used by the current Open Field module:

- `bodyparts`: frame number.
- `leftforword_x`, `leftforword_y`
- `rightforword_x`, `rightforword_y`
- `midbody_x`, `midbody_y`
- `leftback_x`, `leftback_y`
- `leftknee_x`, `leftknee_y`
- `rightback_x`, `rightback_y`
- `rightknee_x`, `rightknee_y`

Recommended future convention:

- Keep coordinates in pixels unless a calibration coefficient is available.
- Add `likelihood` columns later if data comes from DeepLabCut or a similar pose estimator.
- Keep one row per frame and one pair of `x/y` columns per body point.

## 5. Future Multicomponent Analysis Format

For Kalman filtering and neural network experiments, the ideal internal table is:

- `frame`
- `group`
- `day`
- `rat_id`
- `body_point`
- `x`
- `y`
- `likelihood`
- `source_file`

This long format is easier to aggregate, filter, visualize, and feed into models.
