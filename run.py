import os

import numpy as np
import pandas as pd

N_cond = ['Intact', 'SCI_3_dpi', 'SCI_TMT_3_dpi', 'SCI_7_dpi', 'SCI_TMT_7_dpi', 'SCI_14_dpi', 'SCI_TMT_14_dpi',
          'SCI_21_dpi',
          'SCI_TMT_21_dpi', 'SCI_28_dpi', 'SCI_TMT_28_dpi']


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





total_time_steps = []

temp_total_count_steps = 0
temp_total_time_steps = []
temp_total_angels_max = []
temp_total_angels_min = []

colors = {
    1: "red",
    2: "blue",
    3: "green",
    4: "yellow",
    5: "orange",
    6: "purple",
    7: "brown",
    8: "pink",
    9: "turquoise",
    10: "gray"
}

params_for_video = {}

data_csv = pd.read_csv("data/Result_SCI_7.csv", usecols=['Group', 'Number Rat',
                                                         'Step Distance', 'Angle Distance'])
columns = ['Group', 'Day', 'Number Rat',
           'Step Params', 'Angle Params',
           'Count Step', 'Average Time Step', 'Total Time Step(%)',
           'Step Height', 'Max Angel', 'Min Angel']
result_csv_data = []
for index, row in data_csv.iterrows():
    key = row['Group'] + "_" + str(row['Number Rat'])
    params_for_video[key] = [row['Step Distance'], row['Angle Distance']]

for cond_idx in range(0, len(N_cond)):  # Loop through the elements of an object 0 to N-1
    cond = cond_idx  # Use consistent variable types for indexing
    cond_dir = os.path.join('data/', N_cond[cond])  # Directory for this condition
    fdir = os.path.join(cond_dir, '*_angles.csv')  # File for each condition
    # fdir = str(fdir) #Cast values to string so they are of the same object type
    fnames = [f for f in os.listdir(cond_dir) if
              f.endswith('_angles.csv')]  # List all angle filenames from a directory.

    for n, fname in enumerate(fnames):

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

        for i in range(0, len(result) - 2, 3):
            temp_total_time_steps.append(result[i + 2] - result[i])
            temp_total_angels_max.append(valid_data[result[i]])
            temp_total_angels_max.append(valid_data[result[i + 2]])
            temp_total_angels_min.append(valid_data[result[i + 1]])

        temp = []

        # Добавление группы
        if fname.split("_")[1] != "TMT":
            temp.append(fname.split("_")[0])
        else:
            temp.append(fname.split("_")[0] + "_" + fname.split("_")[1])

        # Добавление дня
        # Добавление номер крысы
        if fname.split("_")[0] == "Intact":
            temp.append(None)
            temp.append(fname.split("_")[1])
        elif fname.split("_")[1] == "TMT":
            temp.append(fname.split("_")[2])
            temp.append(fname.split("_")[4])
        else:
            temp.append(fname.split("_")[1])
            temp.append(fname.split("_")[3])

        temp.append(params_for_video[fname.split("_angles")[0]][0])
        temp.append(params_for_video[fname.split("_angles")[0]][1])

        # Добавление количества шагов
        temp.append(len(temp_total_time_steps))

        # Среднее время шага
        if temp_total_time_steps:
            temp.append(sum(temp_total_time_steps) / len(temp_total_time_steps))
        else:
            temp.append(0)

        # Процент нашагивания
        if temp_total_time_steps:
            temp.append(sum(temp_total_time_steps) / len(valid_data) * 100)
        else:
            temp.append(0)

        # Высота шага
        if temp_total_time_steps:
            temp.append(0)
        else:
            temp.append(0)

        if temp_total_angels_max:
            temp.append(sum(temp_total_angels_max) / len(temp_total_angels_max))
        else:
            temp.append(None)

        if temp_total_angels_min:
            temp.append(sum(temp_total_angels_min) / len(temp_total_angels_min))
        else:
            temp.append(None)

        result_csv_data.append(temp)
        temp_total_angels_max = []
        temp_total_angels_min = []
        temp_total_time_steps = []

pd.DataFrame(result_csv_data, columns=columns).to_csv("Result.csv")
