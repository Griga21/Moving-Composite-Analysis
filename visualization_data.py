import numpy as np
from matplotlib import pyplot as plt

from algoritms import porodi
from multi_thresh_1_test_cell_positions import multi_threash


def build_plots(data_init, tbl, cond_dir):
    data = data_init[1:]
    data = data.astype(np.float64)
    plt.title(cond_dir)
    # Plot the normalized data
    # for p in range(Np):  # Use 0 based indexing for loop
    # Normalize and plot the data. NaNs are handled inside the function
    column_data = data[0:, 2]
    # Slice the array to collect the data for this axis
    column_data = np.array(column_data)
    column_data = column_data.astype(np.float64)

    valid_data = column_data[~np.isnan(column_data)]  # Remove NaN values for calculation
    if valid_data.size == 0:
        print(f"Warning: All values in data[:, 2] are NaN. Skipping normalization and plotting.")
        # continue  # Skip to the next value of p

    mean_val = np.mean(valid_data)
    std_val = np.std(valid_data)

    if std_val == 0:
        print(f"Warning: Standard deviation of data[:, 2] is 0. Skipping normalization and plotting.")
        # continue  # Skip to the next value of p

    X_raw = (column_data - mean_val) / std_val  # Normalize the data

    #analog_result(X_raw, p, N_join[p])  # решение через Фурье

    plt.xlabel(data_init[0, 2])
    multi_threash(X_raw)
    #plt.show()
    return porodi(X_raw)

def build_hist(total_count_steps, total_time_steps):
    fig, axes = plt.subplots(6, 2)

    axes[0, 0].hist(np.array(total_count_steps[0]), bins= 20,label="Intact", edgecolor = 'black' )
    axes[0, 0].legend()
    axes[0, 0].grid(True)

    axes[1, 0].hist(np.array(total_count_steps[0]), label="SCI_3", edgecolor = 'black')
    axes[1, 0].legend()
    axes[1, 0].grid(True)

    axes[1, 1].hist(np.array(total_count_steps[1]), label="SCI_TMT_3", edgecolor = 'black')
    axes[1, 1].legend()
    axes[1, 1].grid(True)

    axes[2, 0].hist(np.array(total_count_steps[2]), label="SCI_7", edgecolor = 'black')
    axes[2, 0].legend()
    axes[2, 0].grid(True)

    axes[2, 1].hist(np.array(total_count_steps[3]), label="SCI_TMT_7", edgecolor = 'black')
    axes[2, 1].legend()
    axes[2, 1].grid(True)

    axes[3, 0].hist(np.array(total_count_steps[4]), label="SCI_14", edgecolor = 'black')
    axes[3, 0].legend()
    axes[3, 0].grid(True)

    axes[3, 1].hist(np.array(total_count_steps[5]), label="SCI_TMT_14", edgecolor = 'black')
    axes[3, 1].legend()
    axes[3, 1].grid(True)

    axes[4, 0].hist(np.array(total_count_steps[6]), label="SCI_21", edgecolor = 'black')
    axes[4, 0].legend()
    axes[4, 0].grid(True)

    axes[4, 1].hist(np.array(total_count_steps[7]), label="SCI_TMT_21", edgecolor = 'black')
    axes[4, 1].legend()
    axes[4, 1].grid(True)

    axes[5, 0].hist(np.array(total_count_steps[8]), label="SCI_28", edgecolor = 'black')
    axes[5, 0].legend()
    axes[5, 0].grid(True)

    axes[5, 1].hist(np.array(total_count_steps[9]), label="SCI_TMT_28", edgecolor = 'black')
    axes[5, 1].legend()
    axes[5, 1].grid(True)

    fig.suptitle("count steps")

    fig, axes_time = plt.subplots(6, 2)

    axes_time[0, 0].hist(np.array(total_time_steps[0]), label="Intact")
    axes_time[0, 0].legend()
    axes_time[0, 0].grid(True)

    axes_time[1, 0].hist(np.array(total_time_steps[0]), label="SCI_3")
    axes_time[1, 0].legend()
    axes_time[1, 0].grid(True)

    axes_time[1, 1].hist(np.array(total_time_steps[1]), label="SCI_TMT_3")
    axes_time[1, 1].legend()
    axes_time[1, 1].grid(True)

    axes_time[2, 0].hist(np.array(total_time_steps[2]), label="SCI_7")
    axes_time[2, 0].legend()
    axes_time[2, 0].grid(True)

    axes_time[2, 1].hist(np.array(total_time_steps[3]), label="SCI_TMT_7")
    axes_time[2, 1].legend()
    axes_time[2, 1].grid(True)

    axes_time[3, 0].hist(np.array(total_time_steps[4]), label="SCI_14")
    axes_time[3, 0].legend()
    axes_time[3, 0].grid(True)

    axes_time[3, 1].hist(np.array(total_time_steps[5]), label="SCI_TMT_14")
    axes_time[3, 1].legend()
    axes_time[3, 1].grid(True)

    axes_time[4, 0].hist(np.array(total_time_steps[6]), label="SCI_21")
    axes_time[4, 0].legend()
    axes_time[4, 0].grid(True)

    axes_time[4, 1].hist(np.array(total_time_steps[7]), label="SCI_TMT_21")
    axes_time[4, 1].legend()
    axes_time[4, 1].grid(True)

    axes_time[5, 0].hist(np.array(total_time_steps[8]), label="SCI_28")
    axes_time[5, 0].legend()
    axes_time[5, 0].grid(True)

    axes_time[5, 1].hist(np.array(total_time_steps[9]), label="SCI_TMT_28")
    axes_time[5, 1].legend()
    axes_time[5, 1].grid(True)

    fig.suptitle("time steps")
    plt.show()
    

def build_boxplots(total_count_steps):
    fig, ax = plt.subplots()
    ax.set_ylabel('Count steps in window')

    bplot = ax.boxplot(total_count_steps,
                       patch_artist=True, label= ['Intact', 'SCI_3_dpi', 'SCI_TMT_3_dpi', 'SCI_7_dpi', 'SCI_TMT_7_dpi', 'SCI_14_dpi', 'SCI_TMT_14_dpi',
          'SCI_21_dpi', 'SCI_TMT_21_dpi', 'SCI_28_dpi', 'SCI_TMT_28_dpi'])
    plt.show()# will be used to label x-ticks

