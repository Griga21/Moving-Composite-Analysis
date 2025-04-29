import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.signal import find_peaks
from statsmodels.sandbox.tsa import movmean

from algoritms import analog_result

N_join = ['elbow', 'hip', 'knee', 'ankle']
N_cond = ['Intact', 'SCI_3_dpi', 'SCI_TMT_3_dpi', 'SCI_7_dpi', 'SCI_TMT_7_dpi', 'SCI_14_dpi', 'SCI_TMT_14_dpi', 'SCI_21_dpi',
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

# Function Definitions
def read_data(cond_dir, fname):
    """Reads rotation angles and magnitudes, handling potential errors."""
    try:
        data = np.loadtxt("D:\Diplom\DiplomPy\data\Intact\Intact_1_angles.csv", delimiter=',', dtype=str)  # Assuming CSV with commas
        magnitudes_fname = fname[:-10] + 'magnitudes.csv' #Removing the _angles part
        tbl = np.loadtxt(os.path.join(cond_dir, magnitudes_fname), delimiter=',', dtype=str) # Assuming CSV with commas
        return data, tbl
    except (FileNotFoundError, ValueError) as e:
        print(f"Error reading {e}")
        return None, None

def analyze_data(data, tbl, idx_out, Np, TypeColor):
    """Analyzes and plots the data, handling potential errors, cleaning and peak detection"""
    if data is None or tbl is None:
        return # Exit if data couldn't be loaded
    try:
        # Data cleaning (commented out in the original MATLAB code):
        # It might be better to perform this cleaning on the tbl data
        # before it's returned by `read_data`, but I've left it in here
        # to match the structure of the original code.
        #for k in range(tbl.shape[1]): # Iterate over columns; Python uses 0-based indexing
        #   mask = outlier_mask(tbl[:,k]) # Replace with the proper Python outlier function
        #   tbl[mask,k] = np.nan
        #   data[mask, idx_out[k]] = np.nan # Make sure idx_out indexing aligns (0 vs. 1-based indexing)

        # Setup figure for plotting raw data
        fig, axes = plt.subplots(4, 1, sharex=True) # Create a set of subplots
        fig.subplots_adjust(hspace=0, wspace=0)

        X_raw = [None] * Np  # Initialize X_raw
        S1 = len(data)
        # Plot the normalized data
        for p in range(Np): #Use 0 based indexing for loop
            # Normalize and plot the data. NaNs are handled inside the function
            column_data = data[1:, p]  # Slice the array to collect the data for this axis
            column_data = np.array(column_data)
            column_data = column_data.astype(np.float64)
            # Omit NaN values for mean and std calculation. NumPy handles this easily.
            valid_data = column_data[~np.isnan(column_data)]  # Remove NaN values for calculation
            valid_data = movmean(valid_data, 200)
            if valid_data.size == 0:
                print(f"Warning: All values in data[:, {p}] are NaN. Skipping normalization and plotting.")
                continue  # Skip to the next value of p

            mean_val = np.mean(valid_data)
            std_val = np.std(valid_data)

            if std_val == 0:
                print(f"Warning: Standard deviation of data[:, {p}] is 0. Skipping normalization and plotting.")
                continue  # Skip to the next value of p

            X_raw[p] = (column_data - mean_val) / std_val  # Normalize the data

            # Plot the data with the specified color
            color = TypeColor[p, :]  # Get the color for this plot type

            axes[p].plot(X_raw[p], color=color, linewidth=1)
            axes[p].set_ylabel(N_join[p] +"1")  # Set title to name of the join
            axes[p].set_xlim([0, S1])
            #Ensure all axes are consistent
        #link_axes(axes)
        #fig.show() #Display Figure

        # Gradient estimation
        M = np.arange(0.3, 0.8, 0.1) # From 0.3 to 0.7 inclusive, in steps of 0.1
        lm = len(M)

        X_sel = np.empty((lm, Np), dtype=object)  # Store the indices of data
        T = np.empty((lm, Np), dtype=object)
        band_init = np.empty((lm, Np), dtype=object)
        band_term = np.empty((lm, Np), dtype=object)
        band_span = np.empty((lm, Np), dtype=object)
        std_span = np.full((lm, Np), np.nan) # Store numerical array not an array of lists
        band_intl = np.empty((lm, Np), dtype=object)
        std_intl = np.full((lm, Np), np.nan) # Store numerical array not an array of lists

        for p in range(Np):
            grad_X = X_raw[p] # Get the correct X_raw data
            S_X = np.std(grad_X[~np.isnan(grad_X)]) #Handle the NaN
            grad_X = grad_X / S_X  # Normalize grad_X (handle NaN in gradient)

            for m in range(lm):
                T[m, p] = np.std(grad_X[~np.isnan(grad_X)]) * M[m] #Standard deviation by which to choose minima and maxima

                # Positive gradient - FIND PEAKS
                X_pos_peaks, _ = find_peaks(grad_X, height=T[m, p]) # Finding peaks
                X_neg_peaks, _ = find_peaks(-grad_X, height=T[m, p]) # Finding negative peaks for other axis analysis
                # Find the indices of the positive and negative gradients
                X_pos_init = X_pos_peaks
                X_pos_term = X_pos_peaks + 1 #For now they are assumed to be one long.
                X_neg_init = X_neg_peaks
                X_neg_term = X_neg_peaks + 1 #For now they are assumed to be one long.
                nt_p = min(len(X_pos_init),len(X_pos_term))

                # Create new arrays to apply to gradient information
                D_pos = np.full(S1, False, dtype=bool)
                for j in range(min(nt_p, len(X_pos_init))): #Apply found minima/maxima locations to an array
                    D_pos[X_pos_init[j]] = 1
                D_neg = np.full(S1, False, dtype=bool)
                for j in range(min(nt_p, len(X_neg_init))):
                    D_neg[X_neg_init[j]] = 1

                # Setup values for filtering
                t = 0
                X_sel[m, p] = np.full(S1, False, dtype=bool) #Set flag values
                band_init[m, p] = [] #Initialize array to find
                band_term[m, p] = []

                for i in range(1, S1 - 1):  # Iterate through the range
                    if not X_sel[m, p][i - 1]:
                        if D_pos[i]:
                            X_sel[m, p][i] = 1
                            t += 1
                            band_init[m, p].append(i)
                    else:
                        if not D_neg[i]:
                            X_sel[m, p][i] = 1
                        else:
                            band_term[m, p].append(i)

                # Handle differences in array length
                if len(band_init[m, p]) > len(band_term[m, p]):
                    X_sel[m, p][band_init[m, p][-1]:] = 0
                    band_init[m, p] = band_init[m, p][:-1]

                # Compute new variables for data filtration
                band_span[m, p] = np.array(band_term[m, p]) - np.array(band_init[m, p])

                std_span[m, p] = np.std(band_span[m, p]) / len(band_span[m, p]) if len(band_span[m, p]) > 0 else np.nan

                band_intl[m, p] = np.array(band_init[m, p][1:]) - np.array(band_term[m, p][:-1])

                std_intl[m, p] = np.std(band_intl[m, p]) / len(band_intl[m, p]) if len(band_intl[m, p]) > 0 else np.nan

                for rank in range(len(band_span[m, p])):
                    band_init_trial = band_init[m, p].copy()
                    band_term_trial = band_term[m, p].copy()
                    X_sel_trial = X_sel[m, p].copy()

                    band_span_indx = np.argsort(band_span[m, p])[::-1] #Correcting the array sort call
                    t = band_span_indx[rank]

                    for i in range(band_init[m, p][t] + 1, band_term[m, p][t]):  # Iterate from band init
                        if D_pos[i]:
                            X_sel_trial[band_init_trial[t]:i - 1] = 0
                            band_init_trial[t] = i

                            band_span_trial = np.array(band_term_trial) - np.array(band_init_trial)
                            std_span_trial = np.std(band_span_trial) / len(band_span_trial) if len(band_span_trial) > 0 else np.nan

                            band_intl_trial = np.array(band_init_trial[1:]) - np.array(band_term_trial[:-1])
                            std_intl_trial = np.std(band_intl_trial) / len(band_intl_trial) if len(band_intl_trial) > 0 else np.nan

                            if std_span_trial < std_span[m, p]:
                                band_init[m, p] = band_init_trial
                                band_term[m, p] = band_term_trial

                                band_span[m, p] = band_span_trial
                                band_intl[m, p] = band_intl_trial

                                std_span[m, p] = std_span_trial
                                std_intl[m, p] = std_intl_trial

                                X_sel[m, p] = X_sel_trial
        # Select from the variables initialized to store the local maxima
        im_front = np.nanargmin(np.nanmean(np.array([std_span[m, 0],std_span[m, 1]]) / np.array([std_intl[m, 0],std_intl[m, 1]]), axis = 0)) if len(std_intl) > 0 else 0 #Check the number of elements to see if it can be minimized over axis
        im_hind = np.nanargmin(np.nanmean(np.array([std_span[m, 2],std_span[m, 3]]) / np.array([std_intl[m, 2],std_intl[m, 3]]), axis = 0)) if len(std_intl) > 0 else 0

        #Check the index array to see if it is empty or not
        if len(std_intl) > 0:
            im = [im_front, im_front, im_hind, im_hind]
        else:
            im = [0,0,0,0]
        #Create new figure for plotting and visualizing final data output
        fig_filter, axes_filter = plt.subplots(4, 1, sharex=True)  # Creates figure for the output visualization
        fig_filter.subplots_adjust(hspace=0, wspace=0)

        for p in range(Np): # Now we draw all of the lines for the final visualizations
            #plot(grad_X,'Color','#7E2F8E');   hold on
            axes_filter[p].axhline(0, color='k', linestyle='--') # Horizontal line function

            axes_filter[p].axhline(T[im[p],p], color='g') # Plot green at 1 STD away
            axes_filter[p].axhline(-T[im[p],p], color='g')  # Plot other standard deviation bounds

            axes_filter[p].plot(X_sel[im[p],p], color='k', linewidth=1) # Select appropriate array values
            axes_filter[p].set_ylabel(N_join[p])

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

            # Plot the data with the specified color
            color = TypeColor[p, :]  # Get the color for this plot type

            axes_filter[p].plot(X_raw[p], color=color, linewidth=1)
            axes_filter[p].set_ylabel(N_join[p])  # Set title to name of the join
            axes_filter[p].set_xlim([0, S1])
            #plt.show() #Show figures after they are computed
    except Exception as e:
        print(f"Error during analysis: {e}")

# Main Loop
for cond_idx in range(10,len(N_cond)): #Loop through the elements of an object 0 to N-1
    cond = cond_idx #Use consistent variable types for indexing
    cond_dir = os.path.join('./data/', N_cond[cond])  # Directory for this condition
    fdir = os.path.join(cond_dir, '*_angles.csv') #File for each condition
    #fdir = str(fdir) #Cast values to string so they are of the same object type
    fnames = [f for f in os.listdir(cond_dir) if f.endswith('_angles.csv')]  # List all angle filenames from a directory.

    for n, fname in enumerate(fnames):
        data_init = np.loadtxt(os.path.join(cond_dir, fname), delimiter=',', dtype=str)
        data = data_init[1:]
        data = data.astype(np.float64)
        column_data = data[0:, 3]
        column_data = np.array(column_data)
        column_data = column_data.astype(np.float64)

        valid_data = column_data[~np.isnan(column_data)]
        analog_result(valid_data, "Intact")
        plt.show()
# After the loops, keep the figures open
