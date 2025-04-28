import numpy as np


def local_extrema_windowed(signal, window_size=7, mode='max'):
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


def count_steps(self, local_data):
    peaks_max = local_extrema_windowed(local_data)

    peaks_min = local_extrema_windowed(local_data, mode="min")

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
                if abs(local_data[temp_array[i]] - local_data[result[-1]]) > self.spinbox_angle.value():
                    result.append(temp_array[i])
                    prev_min = True
                else:
                    result.pop()
                    start_step = False
            elif temp_array[i] < result[-1] and not prev_min:
                result.pop()
                result.append(temp_array[i])
        elif start_step and prev_min and temp_array[i] in peaks_max:
            if temp_array[i] - result[-1] < self.spinbox_step.value():
                result.append(temp_array[i])
                start_step = False
            else:
                result.pop()
                result.pop()
                result.append(temp_array[i])
                start_step = True
            prev_min = False

    temp_result = np.zeros(len(self.valid_data))
    for i in range(0, len(result) - 2, 3):
        for j in range(result[i], result[i + 2] + 1):
            temp_result[j] = self.valid_data[result[i]]
    return temp_result
