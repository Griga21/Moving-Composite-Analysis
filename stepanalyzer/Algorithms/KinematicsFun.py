import os

import numpy as np


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


def definition_step_cycle(cond_dir, params_for_video, fname):
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
    return result
