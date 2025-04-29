import numpy as np
from matplotlib import pyplot as plt
from scipy.fft import fft
from scipy.signal import correlate



def normalize_data(average_value_arr, data, dt):
    sum_data_value = 0
    for i in range(0, len(data) - dt, dt):
        subArr = np.std(data[i:i + dt])
        for j in range(i, i + dt):
            data[j] = data[j] / subArr
            sum_data_value += data[j]
        average_value_arr.append(sum_data_value / dt)
        sum_data_value = 0
    #plt.plot(data)
    return data


def analog_result(X_raw, titel):
    fig, axes = plt.subplots(3, 2, figsize=(17, 8))

    axes[0, 0].plot(X_raw, label="signal")
    axes[0, 0].set_title('signal')
    axes[0, 0].legend()

    axes[0, 1].plot(fft(X_raw), label="spector")
    axes[0, 1].set_title('spector')
    axes[0, 1].legend()

    X_raw = correlate(X_raw, X_raw)
    axes[1, 0].plot(X_raw, label="spector")
    axes[1, 0].set_title('acorr')
    axes[1, 0].legend()

    axes[1, 1].plot(fft(X_raw), label="spector")
    axes[1, 1].set_title('spector')
    axes[1, 1].legend()

    X_raw = correlate(X_raw, X_raw)

    axes[2, 0].plot(X_raw, label="spector")
    axes[2, 0].set_title('acorr2')
    axes[2, 0].legend()

    axes[2, 1].plot(fft(X_raw), label="spector")
    axes[2, 1].set_title('spector')
    axes[2, 1].legend()
    fig.suptitle(f'{titel}', fontsize=16)


def porodi(X_raw):
    data = X_raw

    average_value_arr = []  # средние значения с учетом частоты дискр.
    dt = 60  # freq

    #data = delete_VCH(data)
    data = normalize_data(average_value_arr, data, dt)

    position = 0
    for i in range(0, len(average_value_arr) - 1):
        plt.plot([position, position + dt], [average_value_arr[i], average_value_arr[i]], color='black')
        plt.plot([position + dt, position + dt], [average_value_arr[i], average_value_arr[i + 1]], color='black')
        position += dt

    temp = 0
    step_arr = []
    raise_grad = True
    temp_peresech = 0
    count_peresech_arr = []
    temp_peresech_arr = []
    time_peresech_arr = []

    for i in range(0, len(data) - dt):
        if i % dt == 0 and i != 0:
            temp += 1
            count_peresech_arr.append(len(temp_peresech_arr))
            temp_peresech_arr.clear()
        if data[i] > average_value_arr[temp] and raise_grad:
            step_arr.append(i)
            raise_grad = False
            temp_peresech = i
        if data[i] < average_value_arr[temp] and not raise_grad:
            raise_grad = True
            if i - temp_peresech > 1:
                step_arr.append(i)
                temp_peresech_arr.append(i - temp_peresech)
            else:
                step_arr.pop()

    for i in range(0, len(step_arr) - 1, 2):
        plt.plot([step_arr[i], step_arr[i + 1]], [1, 1], color='red')
        plt.grid(True)
    return count_peresech_arr, time_peresech_arr
