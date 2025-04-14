import os

import numpy as np
from statsmodels.sandbox.tsa import movmean

from visualization_data import build_plots, build_hist, build_boxplots

N_join = ['elbow', 'hip', 'knee', 'ankle']
N_cond = ['Intact', 'SCI_3_dpi', 'SCI_TMT_3_dpi', 'SCI_7_dpi', 'SCI_TMT_7_dpi', 'SCI_14_dpi', 'SCI_TMT_14_dpi',
          'SCI_21_dpi', 'SCI_TMT_21_dpi', 'SCI_28_dpi', 'SCI_TMT_28_dpi']
Np = len(N_join)


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


total_count_steps = []  # массив массивов с количество шагов на интервале для всех групп
total_time_steps = []

for cond_idx in range(0, len(N_cond)):  # Loop through the elements of an object 0 to N-1
    cond = cond_idx  # Use consistent variable types for indexing
    cond_dir = os.path.join('./', N_cond[cond])  # Directory for this condition
    fdir = os.path.join(cond_dir, '*_angles.csv')  # File for each condition

    fnames = [f for f in os.listdir(cond_dir) if
              f.endswith('_angles.csv')]  # List all angle filenames from a directory.

    total_counet_steps_temp = []  # массив для одной группы
    total_time_steps_temp = []

    for n, fname in enumerate(fnames):
        data, tbl = read_data(cond_dir, fname)
        # total_counet_steps_temp.extend(build_plots(data, tbl, cond_dir))
        x, y = build_plots(data, tbl, cond_dir)
        total_counet_steps_temp.extend(x)
        total_time_steps_temp.extend(y)

    total_count_steps.append(total_counet_steps_temp)
    total_time_steps.append(total_time_steps_temp)
#build_boxplots(total_count_steps)
#build_hist(total_count_steps, total_time_steps)
