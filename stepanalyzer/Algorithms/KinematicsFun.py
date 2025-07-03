import os

import numpy as np

from stepanalyzer.Algorithms.ReadDataFile import read_csv_coordinate


def moving_average(signal, window_size):
    return np.convolve(signal, np.ones(window_size) / window_size, mode='same')


def local_extrema_windowed(signal, window_size=15, mode='max'):
    half = window_size // 2
    extrema_indices = []

    for i in range(half, len(signal) - half):
        window = signal[i - half:i + half + 1]
        center = signal[i]

        if mode == 'max' and center == np.max(window):
            extrema_indices.append(i)
        elif mode == 'min' and center == np.min(window):
            extrema_indices.append(i)

    return extrema_indices


def definition_step_cycle(cond_dir, fname, params_for_video):
    """Func for definition step cycle.
    @:param cond_dir - directory of the file path
    @:param params_for_video - params of step distance and angel
    @:param fname - file name
    @:return dict{Group+Number_Rut:[Step Params, Angle Distance]}
    """
    data_init = np.loadtxt(os.path.join(cond_dir, fname), delimiter=',', dtype=str)
    data = data_init[1:]
    data = data.astype(np.float64)
    column_data = data[0:, 3]
    column_data = np.array(column_data)
    column_data = column_data.astype(np.float64)

    valid_data = column_data[~np.isnan(column_data)]

    valid_data = moving_average(valid_data, 7)
    peaks_max = local_extrema_windowed(valid_data)
    peaks_min = local_extrema_windowed(valid_data, mode="min")

    average_min = 0
    average_max = 0

    if peaks_max and peaks_min:
        average_max = average_angle(peaks_max, valid_data)
        average_min = average_angle(peaks_min, valid_data)

    if average_max < average_min:
        print(f'Ошибка в расчетах в файле {fname}')

    result = []
    temp_array = []
    temp_array.extend(peaks_max)
    temp_array.extend(peaks_min)
    temp_array.sort()

    prev_min = False
    start_step = False

    for i in range(0, len(temp_array)):
        if not start_step and not prev_min and temp_array[i] in peaks_max:
            result.append(temp_array[i])
            prev_min = False
            start_step = True
        elif start_step and not prev_min:
            if temp_array[i] in peaks_min:
                if abs(valid_data[temp_array[i]] - valid_data[result[-1]]) > \
                        params_for_video.get(fname.split("_angles")[0])[1]:
                    result.append(temp_array[i])
                    prev_min = True
                else:
                    result.pop()
                    start_step = False
            elif temp_array[i] < result[-1] and not prev_min:
                result.pop()
                result.append(temp_array[i])
        elif start_step and prev_min and temp_array[i] in peaks_max:
            if temp_array[i] - result[-1] < params_for_video.get(fname.split("_angles")[0])[0]:
                result.append(temp_array[i])
                start_step = False
            else:
                result.pop()
                result.pop()
                result.append(temp_array[i])
                start_step = True
            prev_min = False
    return result, average_max, average_min


def average_angle(list_points, valid_data):
    sum = 0
    for i in range(len(list_points)):
        sum += valid_data[list_points[i]]
    return sum / len(list_points)


def calculate_number_time_steps(list_steps):
    """Read params for all videos.
    @:param path - path to the file with data params
    @:param use_columns - array of use columns
    @:return all count step, average time step
    """
    count_step = 0
    average_time = 0
    if len(list_steps) > 4:
        x = 0
        if list_steps[0] < list_steps[1]:
            x = 1
        for i in range(x, len(list_steps) - 2, 3):
            average_time += list_steps[i + 2] - list_steps[i]
            count_step += 1
        return count_step, average_time / count_step
    else:
        return 0, 0


def calculate_average_height(list_steps, data_path):
    coordinates = read_csv_coordinate(data_path, "toe_y")
    for i in range(0, len(list_steps), 2):
        print(i)
    return None
