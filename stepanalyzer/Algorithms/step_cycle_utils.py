import numpy as np


def moving_average(signal, window_size):
    return np.convolve(signal, np.ones(window_size) / window_size, mode="same")


def local_extrema_windowed(signal, window_size=15, mode="max"):
    half = window_size // 2
    extrema_indices = []

    for index in range(half, len(signal) - half):
        window = signal[index - half:index + half + 1]
        center = signal[index]

        if mode == "max" and center == np.max(window):
            extrema_indices.append(index)
        elif mode == "min" and center == np.min(window):
            extrema_indices.append(index)

    return extrema_indices


def merge_extrema(peaks_max, peaks_min):
    extrema = list(peaks_max)
    extrema.extend(peaks_min)
    extrema.sort()
    return extrema


def build_step_cycle(
    valid_data,
    peaks_max,
    peaks_min,
    step_distance,
    angle_distance,
    use_previous_peak_for_step=False,
):
    result = []
    prev_min = False
    start_step = False

    for point in merge_extrema(peaks_max, peaks_min):
        if not start_step and not prev_min and point in peaks_max:
            result.append(point)
            prev_min = False
            start_step = True
        elif start_step and not prev_min:
            if point in peaks_min:
                if abs(valid_data[point] - valid_data[result[-1]]) > angle_distance:
                    result.append(point)
                    prev_min = True
                else:
                    result.pop()
                    start_step = False
            elif point < result[-1]:
                result.pop()
                result.append(point)
        elif start_step and prev_min and point in peaks_max:
            anchor_index = -2 if use_previous_peak_for_step else -1

            if point - result[anchor_index] < step_distance:
                result.append(point)
                start_step = False
            else:
                result.pop()
                result.pop()
                result.append(point)
                start_step = True

            prev_min = False

    return result


def extract_valid_signal(raw_signal):
    return raw_signal[~np.isnan(raw_signal)]


def parse_result_identity(file_stem):
    parts = file_stem.split("_")

    if parts[0] == "Intact":
        return parts[0], None, parts[1]

    if len(parts) > 1 and parts[1] == "TMT":
        return f"{parts[0]}_{parts[1]}", parts[2], parts[4]

    return parts[0], parts[1], parts[3]
