import os

import numpy as np

from stepanalyzer.Algorithms.ReadDataFile import read_csv_coordinate
from stepanalyzer.Algorithms.step_cycle_utils import (
    build_step_cycle,
    extract_valid_signal,
    local_extrema_windowed,
    moving_average,
)


def definition_step_cycle(cond_dir, fname, params_for_video):
    """Func for definition step cycle.
    @:param cond_dir - directory of the file path
    @:param params_for_video - params of step distance and angel
    @:param fname - file name
    @:return dict{Group+Number_Rut:[Step Params, Angle Distance]}
    """
    data_init = np.loadtxt(os.path.join(cond_dir, fname), delimiter=",", dtype=str)
    data = data_init[1:]
    data = data.astype(np.float64)
    column_data = data[0:, 3]
    column_data = np.array(column_data)
    column_data = column_data.astype(np.float64)

    valid_data = extract_valid_signal(column_data)
    valid_data = moving_average(valid_data, 7)
    peaks_max = local_extrema_windowed(valid_data)
    peaks_min = local_extrema_windowed(valid_data, mode="min")

    average_min = 0
    average_max = 0

    if peaks_max and peaks_min:
        average_max = average_angle(peaks_max, valid_data)
        average_min = average_angle(peaks_min, valid_data)

    if average_max < average_min:
        print(f"РћС€РёР±РєР° РІ СЂР°СЃС‡РµС‚Р°С… РІ С„Р°Р№Р»Рµ {fname}")

    step_distance, angle_distance = params_for_video.get(fname.split("_angles")[0])
    result = build_step_cycle(
        valid_data,
        peaks_max,
        peaks_min,
        step_distance,
        angle_distance,
        use_previous_peak_for_step=True,
    )
    return result, average_max, average_min


def average_angle(list_points, valid_data):
    total = 0
    for point in list_points:
        total += valid_data[point]
    return total / len(list_points)


def calculate_number_time_steps(list_steps):
    """Read params for all videos.
    @:param path - path to the file with data params
    @:param use_columns - array of use columns
    @:return all count step, average time step
    """
    count_step = 0
    average_time = 0
    if len(list_steps) > 4:
        for i in range(0, len(list_steps) - 2, 3):
            average_time += list_steps[i + 2] - list_steps[i]
            count_step += 1
        return count_step, average_time / count_step

    return 0, 0


def calculate_average_height(list_steps, data_path):
    coordinates = read_csv_coordinate(data_path, "toe_y")
    total = 0
    counter = 0
    for i in range(0, len(list_steps) - 1, 3):
        height_delta = coordinates[list_steps[i + 1]] - coordinates[list_steps[i]]
        if height_delta > 0:
            total += height_delta
            counter += 1

    if counter != 0 and total != 0:
        return total / counter

    return 0
