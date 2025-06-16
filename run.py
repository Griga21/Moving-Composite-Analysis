import os

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from pandas.core.interchange.dataframe_protocol import DataFrame
from scipy.ndimage import label

N_join = ['elbow', 'hip', 'knee', 'ankle']
N_cond = ['Intact', 'SCI_3_dpi', 'SCI_TMT_3_dpi', 'SCI_7_dpi', 'SCI_TMT_7_dpi', 'SCI_14_dpi', 'SCI_TMT_14_dpi',
          'SCI_21_dpi',
          'SCI_TMT_21_dpi', 'SCI_28_dpi', 'SCI_TMT_28_dpi']
R_cond = ['Intact', 'SCI_3', 'SCI_7_dpi', 'SCI_14_dpi', 'SCI_21_dpi', 'SCI_28_dpi', ]
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
result_count_steps = {}
result_time_steps = {}
result_angels = {}

temp_total_count_steps = 0
temp_total_time_steps = []
temp_total_angels = []
bar_colors = ['green', 'red', 'blue',
              'red', 'blue', 'red', 'blue'
                                    'red', 'blue', 'red', 'blue']

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
columns = ['Group', 'Number Rat', 'Count Step', 'Average Time Step', 'Average Angel']
result_csv_data = []
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
            temp_total_angels.append(abs(valid_data[result[i]] - valid_data[result[i + 1]]))
            temp_total_angels.append(abs(valid_data[result[i + 1]] - valid_data[result[i + 2]]))

        result_count_steps[fname.split("_angles")[0]] = len(temp_total_time_steps)
        result_time_steps[fname.split("_angles")[0]] = temp_total_time_steps
        result_angels[fname.split("_angles")[0]] = temp_total_angels
        temp = []
        if fname.split("_")[0] != "Intact":
            temp.append(fname.split("_")[0] + " " + fname.split("_")[1] + " " + fname.split("_")[2])
        else:
            temp.append(fname.split("_")[0])

        if fname.split("_")[0] == "Intact":
            temp.append(fname.split("_")[1])
        else:
            if fname.split("_")[1] == "TMT":
                temp.append(fname.split("_")[4])
            else:
                temp.append(fname.split("_")[3])


        temp.append(len(temp_total_time_steps))
        if temp_total_time_steps:
            temp.append(sum(temp_total_time_steps) / len(temp_total_time_steps))
        else:
            temp.append(0)
        if temp_total_angels:
            temp.append(sum(temp_total_angels) / len(temp_total_angels))
        else:
            temp.append(0)
        result_csv_data.append(temp)
        temp_total_angels = []
        temp_total_time_steps = []

pd.DataFrame(result_csv_data, columns=columns).to_csv("Result.csv")
fig3, ax = plt.subplots()
ax.set_ylabel('Количество шагов', size=20)
ax.set_title("Количество шагов по каждому видео", size=20)
temp_i = 0
for i in N_cond:
    count_array = []
    temp_bottom = 0
    for j in result_count_steps.keys():
        if i in j:
            count_array.append(result_count_steps.get(j))
            ax.bar(i, result_count_steps.get(j), bottom=temp_bottom, color=colors[int(j.split("_")[-1])])
            temp_bottom += result_count_steps.get(j)
    temp_i += 1
    total_count_steps.append(count_array)

import matplotlib.patches as mpatches

plt.grid(axis="y")
red_patch = mpatches.Patch(color='red', label='1')
blue_patch = mpatches.Patch(color='blue', label='2')
green_patch = mpatches.Patch(color='green', label='3')
yellow_patch = mpatches.Patch(color='yellow', label='4')
orange_patch = mpatches.Patch(color='orange', label='5')
purple_patch = mpatches.Patch(color='purple', label='6')
brown_patch = mpatches.Patch(color='brown', label='7')
pink_patch = mpatches.Patch(color='pink', label='8')
turquoise_patch = mpatches.Patch(color='turquoise', label='9')
gray_patch = mpatches.Patch(color='gray', label='10')
plt.legend(handles=[
    red_patch, blue_patch, green_patch, yellow_patch, orange_patch,
    purple_patch, brown_patch, pink_patch, turquoise_patch, gray_patch
])

fig1, ax = plt.subplots()
ax.set_ylabel('Total time step')
for i in N_cond:
    time_array = []
    for j in result_time_steps.keys():
        if i in j:
            time_array.extend(result_time_steps.get(j))
    total_time_steps.append(time_array)
bplot = ax.boxplot(total_time_steps,
                   patch_artist=True, tick_labels=N_cond
                   )

fig2, ax = plt.subplots()
ax.set_ylabel('total_angels')
for i in N_cond:
    time_array = []
    for j in result_angels.keys():
        if i in j:
            time_array.extend(result_time_steps.get(j))
    total_angels.append(time_array)
bplot = ax.boxplot(total_angels,
                   patch_artist=True, tick_labels=N_cond
                   )
plt.show()

from scipy.stats import ttest_ind
from scipy.stats import mannwhitneyu

for i in range(1, 11, 2):
    stat, p_value = ttest_ind(total_count_steps[i], total_count_steps[i + 1], equal_var=False)
    print(f'Статистика t: {stat:.4f}, p-value: {p_value:.4f}')
    stat, p_value = mannwhitneyu(total_count_steps[i], total_count_steps[i + 1], alternative='two-sided')
    print(f'Статистика U: {stat:.4f}, p-value: {p_value:.4f}')

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import ttest_ind

# Примерные данные
data = {
    "day": ["Thur"] * 20 + ["Fri"] * 20 + ["Sat"] * 20 + ["Sun"] * 20,
    "value": [12, 15, 13, 10, 14, 13, 18, 19, 17, 16, 15, 14, 13, 15, 14, 17, 18, 16, 19, 17,
              13, 12, 14, 15, 14, 13, 12, 11, 13, 14, 15, 16, 17, 15, 14, 13, 14, 15, 16, 17,
              20, 21, 22, 20, 19, 18, 21, 22, 20, 19, 18, 17, 16, 15, 14, 16, 17, 18, 19, 20,
              15, 14, 16, 17, 13, 12, 15, 16, 17, 18, 16, 15, 14, 13, 12, 15, 16, 17, 18, 19],
    "group": ["Yes"] * 10 + ["No"] * 10 + ["Yes"] * 10 + ["No"] * 10 +
             ["Yes"] * 10 + ["No"] * 10 + ["Yes"] * 10 + ["No"] * 10
}

df = pd.DataFrame(data)

# Построение боксплота
plt.figure(figsize=(10, 6))
sns.boxplot(x="day", y="value", hue="group", data=df)

# Выполнение t-тестов и аннотация
days = df['day'].unique()
for i, day in enumerate(days):
    group_data = df[df['day'] == day]
    yes_vals = group_data[group_data['group'] == 'Yes']['value']
    no_vals = group_data[group_data['group'] == 'No']['value']
    t_stat, p_val = ttest_ind(yes_vals, no_vals)

    # Добавление аннотации
    x1, x2 = i - 0.2, i + 0.2
    y, h = group_data['value'].max() + 2, 1
    plt.plot([x1, x1, x2, x2], [y, y + h, y + h, y], lw=1.5, c='k')
    plt.text((x1 + x2) * .5, y + h + 0.5, f"p < {p_val:.2e}", ha='center', va='bottom')

plt.title("Boxplot by Day and Group with t-test annotations")
plt.legend(title="Group")
plt.tight_layout()
plt.show()
