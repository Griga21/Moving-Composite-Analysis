import os

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks


def multi_threash(signal):
    plt.figure(1)
    plt.clf()
    ax1 = plt.subplot(1, 1, 1)
    plt.plot(signal)
    plt.title('Image Source')

    S1 = np.arange(16, 3, -1)[:, np.newaxis] / signal.shape[1]
    X_grid = [None] * len(S1)
    var_X_grid = np.full(len(S1), np.nan)

    for m in range(len(S1)):
        Y1 = np.convolve(np.mean(signal, axis=0), np.ones(S1[m]) / S1[m], mode='same')
        Y1 = Y1 - np.convolve(Y1, np.ones(S1[m] * 2) / (S1[m] * 2), mode='same')
        Y1 /= np.std(Y1)

        y, x = find_peaks(Y1, distance=S1[m])
        X_grid[m] = x[(y > 0) & (x > S1[m] / 3) & (x < signal.shape[1] - S1[m] / 3)]

        if len(X_grid[m]) > 4:
            var_X_grid[m] = np.var(np.diff(X_grid[m]))

        im_X = np.nanargmin(var_X_grid)
        S1 = S1[im_X]
        X_grid = X_grid[im_X]

        Y1 = np.convolve(np.mean(signal, axis=0), np.ones(S1) / S1, mode='same')
        Y1 = Y1 - np.convolve(Y1, np.ones(S1 * 2) / (S1 * 2), mode='same')
        Y1 /= np.std(Y1)

        ax2 = plt.subplot(1, 1, 1)
        plt.cla()
        plt.plot(Y1)
        plt.axvline(x=X_grid, color='r', linestyle='--')
        plt.title('Processed Data')
        plt.hold(True)

        # plt.figure(2)
        # plt.clf()
        # ax3 = plt.subplot(1, 1, 1)
        # plt.plot(signal, aspect='auto')
        # plt.colorbar()
        # plt.title('Transposed Image Source')
        # plt.hold(True)
        #
        # S2 = np.arange(16, 3, -1)[:, np.newaxis] / signal.shape[0]
        #
        # Y_grid = [None] * len(S2)
        # var_Y_grid = np.full(len(S2), np.nan)
        #
        # for m in range(len(S2)):
        #     Y2 = np.convolve(np.mean(signal, axis=1), np.ones(S2[m]) / S2[m], mode='same')
        #     Y2 = Y2 - np.convolve(Y2, np.ones(S2[m] * 2) / (S2[m] * 2), mode='same')
        #     Y2 /= np.std(Y2)
        #
        #     y, x = find_peaks(Y2, distance=S2[m])
        #     Y_grid[m] = x[(y > 0) & (x > S2[m] / 3) & (x < signal.shape[0] - S2[m] / 3)]
        #
        #     if len(Y_grid[m]) > 4:
        #         var_Y_grid[m] = np.var(np.diff(Y_grid[m]))
        #
        # im_Y = np.nanargmin(var_Y_grid)
        # S2 = S2[im_Y]
        # Y_grid = Y_grid[im_Y]
        #
        # Y2 = np.convolve(np.mean(signal, axis=1), np.ones(S2) / S2, mode='same')
        # Y2 = Y2 - np.convolve(Y2, np.ones(S2 * 2) / (S2 * 2), mode='same')
        # Y2 /= np.std(Y2)

        # ax4 = plt.subplot(1, 1, 1)
        # plt.cla()
        # plt.plot(Y2)
        # plt.axvline(x=Y_grid, color='r', linestyle='--')
        # plt.title('Processed Data Transposed')
        # plt.hold(True)
        #
        # Y_center, X_center = np.meshgrid(Y_grid, X_grid)

        # plt.figure(1)
        # plt.subplot(1, 1, 1)
        # plt.plot(X_center.flatten(), Y_center.flatten(), 'r*')

        # plt.figure(2)
        # plt.subplot(1, 1, 1)
        # plt.plot(Y_center.flatten(), X_center.flatten(), 'r*')

        plt.pause(0.1)

data_init = np.loadtxt(os.path.join('Intact',
                                       'Intact_1_angles.csv'),
                          delimiter=',', dtype=str)
data = data_init[1:]
data = data.astype(np.float64)
column_data = data[0:, 2]
column_data = np.array(column_data)
column_data = column_data.astype(np.float64)

valid_data = column_data[~np.isnan(column_data)]
multi_threash(valid_data)