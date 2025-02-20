import os

import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import fft
from scipy.signal import correlate, find_peaks

N_join = ['elbow', 'hip', 'knee', 'ankle']
N_cond = ['Intact', 'SCI_3_dpi', 'SCI_TMT_3_dpi', 'SCI_7_dpi', 'SCI_TMT_7_dpi', 'SCI_14_dpi', 'SCI_TMT_14_dpi',
          'SCI_21_dpi', 'SCI_TMT_21_dpi', 'SCI_28_dpi', 'SCI_TMT_28_dpi']


Np = len(N_join)


def analog_result(X_raw, p, titel):
    # x = np.arange(0, 5 * np.pi, 0.1)
    # y = np.sin(x)
    # plt.plot(x, y, color='green')
    # signal_sin = correlate(y, y)
    # signal_sin = correlate(signal_sin, signal_sin)
    # signal_sin = fft(signal_sin)
    # peak, _ = find_peaks(signal_sin)
    # plt.plot(signal_sin)

    fig, axes = plt.subplots(3, 2, figsize=(17, 8))

    axes[0, 0].plot(X_raw[p], label="signal")
    axes[0, 0].set_title('signal')
    axes[0, 0].legend()

    axes[0, 1].plot(fft(X_raw[p]), label="spector")
    axes[0, 1].set_title('spector')
    axes[0, 1].legend()

    X_raw[p] = correlate(X_raw[p], X_raw[p])
    axes[1, 0].plot(X_raw[p], label="spector")
    axes[1, 0].set_title('acorr')
    axes[1, 0].legend()

    axes[1, 1].plot(fft(X_raw[p]), label="spector")
    axes[1, 1].set_title('spector')
    axes[1, 1].legend()

    X_raw[p] = correlate(X_raw[p], X_raw[p])

    axes[2, 0].plot(X_raw[p], label="spector")
    axes[2, 0].set_title('acorr2')
    axes[2, 0].legend()

    axes[2, 1].plot(fft(X_raw[p]), label="spector")
    axes[2, 1].set_title('spector')
    axes[2, 1].legend()
    fig.suptitle(f'{titel}', fontsize=16)


def porodi(X_raw, p):
    peaks,_ = find_peaks(X_raw[p], height=(-10, 10))
    plt.plot(X_raw[p])
    plt.plot(peaks, X_raw[p][peaks],"*")
    return


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


def build_plots(data, tbl):
    data = data[1:]
    data = data.astype(np.float64)

    X_raw = [None] * Np  # Initialize X_raw
    S1 = len(data)
    # Plot the normalized data
    for p in range(Np):  # Use 0 based indexing for loop
        # Normalize and plot the data. NaNs are handled inside the function
        column_data = data[1:, p]  # Slice the array to collect the data for this axis
        column_data = np.array(column_data)
        column_data = column_data.astype(np.float64)
        # Omit NaN values for mean and std calculation. NumPy handles this easily.
        valid_data = column_data[~np.isnan(column_data)]  # Remove NaN values for calculation
        if valid_data.size == 0:
            print(f"Warning: All values in data[:, {p}] are NaN. Skipping normalization and plotting.")
            continue  # Skip to the next value of p

        mean_val = np.mean(valid_data)
        std_val = np.std(valid_data)

        if std_val == 0:
            print(f"Warning: Standard deviation of data[:, {p}] is 0. Skipping normalization and plotting.")
            continue  # Skip to the next value of p

        X_raw[p] = (column_data - mean_val) / std_val  # Normalize the data

        #analog_result(X_raw, p, N_join[p])  # решение через Фурье
        porodi(X_raw, p)

        plt.show()
    return None


for cond_idx in range(10, len(N_cond)):  # Loop through the elements of an object 0 to N-1
    cond = cond_idx  # Use consistent variable types for indexing
    cond_dir = os.path.join('./', N_cond[cond])  # Directory for this condition
    fdir = os.path.join(cond_dir, '*_angles.csv')  # File for each condition
    # fdir = str(fdir) #Cast values to string so they are of the same object type
    fnames = [f for f in os.listdir(cond_dir) if
              f.endswith('_angles.csv')]  # List all angle filenames from a directory.

    for n, fname in enumerate(fnames):
        data, tbl = read_data(cond_dir, fname)
        build_plots(data, tbl)
# After the loops, keep the figures open
plt.show()
