import os

from fontTools.misc.cython import returns
from scipy import signal
from collections import deque
from statistics import fmean

import numpy as np
from matplotlib import pyplot as plt
from scipy.signal import find_peaks
from statsmodels.sandbox.tsa import movmean

from algoritms import normalize_data

N_join = ['elbow', 'hip', 'knee', 'ankle']
N_cond = ['Intact', 'SCI_3_dpi', 'SCI_TMT_3_dpi', 'SCI_7_dpi', 'SCI_TMT_7_dpi', 'SCI_14_dpi', 'SCI_TMT_14_dpi',
          'SCI_21_dpi',
          'SCI_TMT_21_dpi', 'SCI_28_dpi', 'SCI_TMT_28_dpi']
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


for cond_idx in range(10, len(N_cond)):  # Loop through the elements of an object 0 to N-1
    cond = cond_idx  # Use consistent variable types for indexing
    cond_dir = os.path.join('./', N_cond[cond])  # Directory for this condition
    fdir = os.path.join(cond_dir, '*_angles.csv')  # File for each condition
    # fdir = str(fdir) #Cast values to string so they are of the same object type
    fnames = [f for f in os.listdir(cond_dir) if
              f.endswith('_angles.csv')]  # List all angle filenames from a directory.

    for n, fname in enumerate(fnames):

        data_init = np.loadtxt(os.path.join("D:\Diplom\DiplomPy\Intact\Intact_1_angles.csv"),
                               delimiter=',', dtype=str)
        data = data_init[1:]
        data = data.astype(np.float64)
        column_data = data[0:, 3]
        column_data = np.array(column_data)
        column_data = column_data.astype(np.float64)

        valid_data = column_data[~np.isnan(column_data)]  # Remove NaN values for calculation
        # plt.plot(valid_data)

        valid_data = moving_average(valid_data, 5)
        plt.plot(valid_data, c="b")

        peaks_max = local_extrema_windowed(valid_data)
        plt.scatter(peaks_max, valid_data[peaks_max])

        peaks_min = local_extrema_windowed(valid_data, mode="min")
        plt.scatter(peaks_min, valid_data[peaks_min])
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
                    if abs(valid_data[temp_array[i]] - valid_data[result[-1]]) > 15:
                        result.append(temp_array[i])
                        prev_min = True
                    else:
                        result.pop()
                        start_step = False
                elif temp_array[i] < result[-1] and not prev_min:
                    result.pop()
                    result.append(temp_array[i])
            elif start_step and prev_min and temp_array[i] in peaks_max:
                    result.append(temp_array[i])

                    start_step = False
                    prev_min = False


    for i in range(0, len(result) - 2, 3):
        plt.plot([result[i], result[i + 2]], [valid_data[result[i]], valid_data[result[i]]], c="r")

    plt.xlabel('Lead Time (in days)')
    plt.ylabel('Proportation of Events Scheduled')
    plt.show()
