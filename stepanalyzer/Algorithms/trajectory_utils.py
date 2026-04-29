import math

import numpy as np
import pandas as pd


FRAME_COLUMN_CANDIDATES = ("frame", "frames", "coords", "bodyparts", "index", "time")


def infer_frame_column(dataframe):
    for column in dataframe.columns:
        if str(column).strip().lower() in FRAME_COLUMN_CANDIDATES:
            return column
    return dataframe.columns[0]


def infer_coordinate_columns(dataframe):
    columns_by_lower = {str(column).strip().lower(): column for column in dataframe.columns}
    coordinates = {}

    for column in dataframe.columns:
        column_name = str(column).strip()
        lower_name = column_name.lower()
        if not lower_name.endswith("_x"):
            continue

        label = column_name[:-2]
        y_column = columns_by_lower.get(f"{label.lower()}_y")
        if y_column is not None:
            coordinates[label] = (column, y_column)

    return coordinates


def read_trajectory_csv(path):
    dataframe = pd.read_csv(path)
    frame_column = infer_frame_column(dataframe)
    coordinates = infer_coordinate_columns(dataframe)

    if not coordinates:
        raise ValueError("CSV file must contain coordinate pairs with columns like point_x and point_y.")

    dataframe[frame_column] = pd.to_numeric(dataframe[frame_column], errors="coerce")
    if dataframe[frame_column].isna().all():
        dataframe[frame_column] = np.arange(len(dataframe))
    else:
        dataframe[frame_column] = dataframe[frame_column].ffill().fillna(0).astype(int)

    for x_column, y_column in coordinates.values():
        dataframe[x_column] = pd.to_numeric(dataframe[x_column], errors="coerce")
        dataframe[y_column] = pd.to_numeric(dataframe[y_column], errors="coerce")

    return dataframe, frame_column, coordinates


def point_speed(dataframe, x_column, y_column, smoothing_window=5):
    x = dataframe[x_column].astype(float).interpolate(limit_direction="both").to_numpy()
    y = dataframe[y_column].astype(float).interpolate(limit_direction="both").to_numpy()

    dx = np.gradient(x)
    dy = np.gradient(y)
    speed = np.sqrt(dx ** 2 + dy ** 2)

    if smoothing_window and smoothing_window > 1 and len(speed) >= smoothing_window:
        kernel = np.ones(smoothing_window) / smoothing_window
        speed = np.convolve(speed, kernel, mode="same")

    return speed


def point_summary(dataframe, coordinates):
    rows = []
    for label, (x_column, y_column) in coordinates.items():
        x = dataframe[x_column].astype(float)
        y = dataframe[y_column].astype(float)
        speed = point_speed(dataframe, x_column, y_column)
        distance = np.nansum(np.sqrt(np.diff(x) ** 2 + np.diff(y) ** 2))
        rows.append(
            {
                "point": label,
                "mean_x": np.nanmean(x),
                "mean_y": np.nanmean(y),
                "mean_speed": np.nanmean(speed),
                "max_speed": np.nanmax(speed),
                "path_length": distance if not math.isnan(distance) else 0,
            }
        )
    return pd.DataFrame(rows)
