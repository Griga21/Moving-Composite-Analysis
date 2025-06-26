import os

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

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