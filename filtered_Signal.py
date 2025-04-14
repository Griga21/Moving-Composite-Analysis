import os

import numpy as np
from matplotlib import pyplot as plt
from statsmodels.sandbox.tsa import movmean

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
        data = np.loadtxt(os.path.join(cond_dir, fname), delimiter=',', dtype=str)  # Assuming CSV with commas
        magnitudes_fname = fname[:-10] + 'magnitudes.csv' #Removing the _angles part
        tbl = np.loadtxt(os.path.join(cond_dir, magnitudes_fname), delimiter=',', dtype=str) # Assuming CSV with commas
        return data, tbl
    except (FileNotFoundError, ValueError) as e:
        print(f"Error reading {e}")
        return None, None


for cond_idx in range(10,len(N_cond)): #Loop through the elements of an object 0 to N-1
    cond = cond_idx #Use consistent variable types for indexing
    cond_dir = os.path.join('./', N_cond[cond])  # Directory for this condition
    fdir = os.path.join(cond_dir, '*_angles.csv') #File for each condition
    #fdir = str(fdir) #Cast values to string so they are of the same object type
    fnames = [f for f in os.listdir(cond_dir) if f.endswith('_angles.csv')]  # List all angle filenames from a directory.

    for n, fname in enumerate(fnames):

        data_init = np.loadtxt(os.path.join(cond_dir,
                                                    fname),
                                       delimiter=',', dtype=str)
        data = data_init[1:]
        data = data.astype(np.float64)
        column_data = data[0:, 3]
        column_data = np.array(column_data)
        column_data = column_data.astype(np.float64)

        valid_data = column_data[~np.isnan(column_data)]  # Remove NaN values for calculation
        plt.plot(valid_data)
        valid_data = movmean(valid_data, 120)

        plt.plot(valid_data)

        plt.xlabel('Lead Time (in days)')
        plt.ylabel('Proportation of Events Scheduled')
        ax = plt.gca()
        ax.invert_xaxis()
        ax.yaxis.tick_right()
        ax.yaxis.set_label_position("right")
        plt.show()
