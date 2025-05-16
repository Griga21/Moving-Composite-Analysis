import os

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

N_join = ['elbow', 'hip', 'knee', 'ankle']
N_cond = ['Intact', 'SCI_3_dpi', 'SCI_TMT_3_dpi', 'SCI_7_dpi', 'SCI_TMT_7_dpi', 'SCI_14_dpi', 'SCI_TMT_14_dpi',
          'SCI_21_dpi',
          'SCI_TMT_21_dpi', 'SCI_28_dpi', 'SCI_TMT_28_dpi']
R_cond = ['Intact', 'SCI_3', 'SCI_7_dpi',  'SCI_14_dpi','SCI_21_dpi', 'SCI_28_dpi',]
N_meth = ['FA0', 'FA1', 'FA2', 'DFA0', 'DFA1', 'DFA2']
idx_out = [1, 1, 2, [2, 3], [2, 3], [3, 4], [3, 4], 4]
S = np.unique(np.concatenate((np.arange(7, 18, 2), np.floor(2 ** np.arange(4.25, 13.25, 0.25)))))
Ns = len(S)
TypeColor = np.array([[0, 0.4470, 0.7410], [0.3010, 0.7450, 0.9330], [0.8500, 0.3250, 0.0980], [1, 0, 0]])
Np = len(N_join)
H_aver = np.full((1, len(N_join), len(N_cond), len(N_meth) + 6), np.nan)
R_aver = np.full((1, len(N_join), len(N_cond), len(N_meth), len(S)), np.nan)
P_aver = np.full((1, len(N_join), len(N_cond), len(N_meth), len(S)), np.nan)


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


def read_data(cond_dir, fname):
    """Reads rotation angles and magnitudes, handling potential errors."""
    try:
        data = np.loadtxt(os.path.join(cond_dir, fname), delimiter=',', dtype=str)  # Assuming CSV with commas
        magnitudes_fname = fname[:-10] + 'magnitudes.csv'  # Removing the _angles part
        tbl = np.loadtxt(os.path.join(cond_dir, magnitudes_fname), delimiter=',', dtype=str)  # Assuming CSV with commas
        return data, tbl
    except (FileNotFoundError, ValueError) as e:
        print(f"Error reading {e}")
        return None, None


total_count_steps = []
total_time_steps = []
total_angels = []

temp_total_count_steps = 0
temp_total_time_steps = []
temp_total_angels = []
bar_colors = ['green', 'red', 'blue',
              'red', 'blue', 'red', 'blue'
                                    'red', 'blue', 'red', 'blue']

params = {'Intact': [30, 15, 7], 'SCI_3_dpi': [30, 7, 20], 'SCI_TMT_3_dpi': [30, 7, 7], 'SCI_7_dpi': [80, 10, 7],
          'SCI_TMT_7_dpi': [80, 10, 7],
          'SCI_14_dpi': [80, 20, 7], 'SCI_TMT_14_dpi': [80, 20, 7], 'SCI_21_dpi': [80, 20, 7],
          'SCI_TMT_21_dpi': [80, 15, 7], 'SCI_28_dpi': [80, 20, 7],
          'SCI_TMT_28_dpi': [50, 20, 7]}
params_for_video = {}

data_csv = pd.read_csv("D:\\Diplom\\DiplomPy\\data\\Result_SCI_7.csv", usecols=['Group', 'Number Rat',
                                                                                'Step Distance', 'Angle Distance'])

for index, row in data_csv.iterrows():
    key = row['Group'] + "_" + str(row['Number Rat'])
    params_for_video[key] = [row['Step Distance'], row['Angle Distance']]

for cond_idx in range(0, len(N_cond)):  # Loop through the elements of an object 0 to N-1
    cond = cond_idx  # Use consistent variable types for indexing
    cond_dir = os.path.join('./data/', N_cond[cond])  # Directory for this condition
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

        valid_data = column_data[~np.isnan(column_data)]  # Remove NaN values for calculation
        # plt.plot(valid_data)

        valid_data = moving_average(valid_data, 7)
        # plt.plot(valid_data, c="b")

        peaks_max = local_extrema_windowed(valid_data)
        # plt.scatter(peaks_max, valid_data[peaks_max])

        peaks_min = local_extrema_windowed(valid_data, mode="min")
        # plt.scatter(peaks_min, valid_data[peaks_min])

        result = []
        temp_array = []
        temp_array.extend(peaks_max)
        temp_array.extend(peaks_min)
        temp_array.sort()

        temp_position_max = 0
        next_temp_position_max = peaks_max[1]
        temp_position_min = peaks_min[0]
        prev_min = False
        start_step = False

        for i in range(0, len(temp_array)):
            if not start_step and not prev_min and temp_array[i] in peaks_max:
                result.append(temp_array[i])
                prev_min = False
                start_step = True
            elif start_step and not prev_min:
                if temp_array[i] in peaks_min:
                    if abs(valid_data[temp_array[i]] - valid_data[result[-1]]) > params_for_video.get(fname.split("_angles")[0])[1]:
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
            # plt.plot([result[i], result[i + 2]], [valid_data[result[i]], valid_data[result[i]]], c="r")
            temp_total_time_steps.append(result[i + 2] - result[i])
            temp_total_angels.append(abs(valid_data[result[i]] - valid_data[result[i + 1]]))
            temp_total_angels.append(abs(valid_data[result[i + 1]] - valid_data[result[i + 2]]))
    temp_total_count_steps = len(temp_total_angels) / 2
    total_count_steps.append(temp_total_count_steps)
    temp_total_count_steps = 0
    total_time_steps.append(temp_total_time_steps)
    temp_total_time_steps = []
    total_angels.append(temp_total_angels)
    temp_total_angels = []

fig1, ax = plt.subplots()
ax.set_ylabel('Total time step')

bplot = ax.boxplot(total_time_steps,
                   patch_artist=True, tick_labels=N_cond
                   )

fig2, ax = plt.subplots()
ax.set_ylabel('total_angels')

bplot = ax.boxplot(total_angels,
                   patch_artist=True, tick_labels=N_cond
                   )


fig3, ax = plt.subplots()
ax.set_ylabel('total_count_step')


ax.bar(N_cond[0], total_count_steps[0], color='g')
i = 1
for j in range(1,11,2):
    if total_count_steps[j+1] > total_count_steps[j]:
        ax.bar(R_cond[i], total_count_steps[j+1], color='b')
        ax.bar(R_cond[i], total_count_steps[j], color='r')
    else:
        ax.bar(R_cond[i], total_count_steps[j], color='r')
        ax.bar(R_cond[i], total_count_steps[j+1], color='b')

    i+=1
plt.grid(axis = "y")
plt.legend(["Intact", "With TMT", "Without TMT"])




sns.set_theme(style="whitegrid")


data_result = [["Intact", "With", total_count_steps[0]],["SCI_3", "With", total_count_steps[2]],["SCI_3", "Without", total_count_steps[1]],
               ["SCI_7", "With", total_count_steps[4]],["SCI_7", "Without", total_count_steps[3]],
               ["SCI_14", "With", total_count_steps[6]],["SCI_14", "Without", total_count_steps[5]],
               ["SCI_21", "With", total_count_steps[8]], ["SCI_21", "Without", total_count_steps[7]],
                ["SCI_28", "With", total_count_steps[10]],["SCI_28", "Without", total_count_steps[9]]]
temp_data = pd.DataFrame(data_result, columns=["Group", "TMT", "count"])

# Draw a nested barplot by species and sex
g = sns.catplot(
    data=temp_data, kind="bar",
    x="Group", y="count", hue="TMT",
    errorbar="sd", palette="dark"
)
g.despine(left=True)
g.set_axis_labels("", "Body mass (g)")
g.legend.set_title("")
plt.show()
