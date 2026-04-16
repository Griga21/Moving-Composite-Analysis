import numpy as np
from stepanalyzer.Algorithms.step_cycle_utils import build_step_cycle, local_extrema_windowed


def count_steps(self, local_data):
    """Form a complex number.

    @:param local_data - array with angels
    @re
    """
    result_array = []
    peaks_max = local_extrema_windowed(local_data)

    peaks_min = local_extrema_windowed(local_data, mode="min")

    result = build_step_cycle(
        local_data,
        peaks_max,
        peaks_min,
        self.spinbox_step.value(),
        self.spinbox_angle.value(),
        use_previous_peak_for_step=True,
    )
    temp_result = np.zeros(len(self.valid_data))
    for i in range(0, len(result) - 2, 3):
        for j in range(result[i], result[i + 2] + 1):
            temp_result[j] = self.valid_data[result[i]]
    return temp_result


def count_average_time_step(step_array):
    average_time_step = 0
    for i in range(0, len(step_array) - 1, 2):
        average_time_step += (step_array[i] + step_array[i + 1]) / 2
    return average_time_step
