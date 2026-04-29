# Visual Direction

## Goal

The interface should feel like a research workstation: calm, dense, and precise. The first screen should help the user quickly choose an analysis mode, open data, inspect trajectories, tune detection parameters, and export results.

## Main Screens

### 1. Start Screen

- Two analysis modes: `Treadmill` and `Open Field`.
- Short dataset status panel: selected video, selected trajectory CSV, selected angle CSV.
- Recent files can be added later.

### 2. Analysis Workspace

Recommended layout:

- Left: video frame with tracked body points.
- Right: synchronized plots.
- Bottom: timeline slider and frame controls.
- Top toolbar: open files, analysis mode, save/export.

For Open Field:

- Use a 2x3 plot grid for body components.
- Add a multicomponent overview plot above or below individual signals.
- Show detected movement intervals as shaded spans, not only lines.

For Treadmill:

- Show raw angle signal and filtered signal together.
- Show detected step cycle start/min/max/end points.
- Keep parameter controls near the plot they affect.

## Visual Language

- Background: light neutral gray.
- Main panels: white, thin borders, small radius.
- Accent colors:
  - Blue: selected frame/current signal.
  - Green: accepted step cycles.
  - Orange: warnings/manual correction.
  - Red: current frame marker or invalid interval.
- Avoid overly decorative colors; the data should be visually dominant.

## Future Visuals For Dissertation

- Coordination matrix: correlation or phase relation between limbs.
- Phase plots: left/right and front/hind limb trajectories.
- Kalman comparison: raw vs filtered coordinates/speeds.
- Recovery timeline: group-level trends across days.
- Neural model summary: confusion matrix and feature importance/proxy sensitivity.
