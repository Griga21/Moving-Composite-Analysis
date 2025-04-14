import csv
import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller


def analyze_window_size_effect(time_series, window_sizes, con_dir, significance_level=0.05):
    """
    Анализирует влияние размера скользящего окна на результаты теста Дики-Фуллера.

    Args:
        time_series (pd.Series): Временной ряд (pandas Series с временным индексом).
        window_sizes (list): Список размеров скользящего окна для анализа.
        significance_level (float): Уровень значимости (альфа).

    Returns:
        pd.DataFrame: DataFrame, содержащий долю стационарных окон для каждого размера окна.
    """

    results = {}
    for window_size in window_sizes:
        p_values = []
        is_stationary = []

        for i in range(len(time_series) - window_size + 1):
            window = time_series[i:i + window_size]
            dftest = adfuller(window, autolag='AIC')
            p_value = dftest[1]
            p_values.append(p_value)
            is_stationary.append(p_value < significance_level)

        stationary_fraction = np.mean(is_stationary)  # Доля стационарных окон
        results[window_size] = stationary_fraction

    results_df = pd.DataFrame.from_dict(results, orient='index', columns=['Доля стационарных окон'])
    results_df.index.name = 'Размер окна'

    # Построение графика

    plt.plot(results_df.index, results_df['Доля стационарных окон'], marker='o')
    plt.title(f'Зависимость доли стационарных окон от размера скользящего окна' + con_dir)
    plt.xlabel('Размер скользящего окна')
    plt.ylabel('Доля стационарных окон')
    plt.grid(True)
    return results_df


N_cond = ['Intact', 'SCI_3_dpi', 'SCI_TMT_3_dpi', 'SCI_7_dpi', 'SCI_TMT_7_dpi', 'SCI_14_dpi', 'SCI_TMT_14_dpi',
          'SCI_21_dpi', 'SCI_TMT_21_dpi', 'SCI_28_dpi', 'SCI_TMT_28_dpi']



data_csv_file= []
data_csv_file.append(['Size window','Intact', 'SCI_3_dpi', 'SCI_TMT_3_dpi', 'SCI_7_dpi', 'SCI_TMT_7_dpi', 'SCI_14_dpi', 'SCI_TMT_14_dpi',
          'SCI_21_dpi', 'SCI_TMT_21_dpi', 'SCI_28_dpi', 'SCI_TMT_28_dpi'])

for cond_idx in range(0, len(N_cond)):  # Loop through the elements of an object 0 to N-1
    cond = cond_idx  # Use consistent variable types for indexing
    cond_dir = os.path.join('./', N_cond[cond])  # Directory for this condition
    fdir = os.path.join(cond_dir, '*_angles.csv')  # File for each condition

    fnames = [f for f in os.listdir(cond_dir) if
              f.endswith('_angles.csv')]  # List all angle filenames from a directory.
    plt.figure(figsize=(10, 6))
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

# 2. Задаем список размеров окна для анализа
        window_sizes = [30, 60, 90, 120, 150, 180, 210, 240, 270]
        data_csv_file.extend([window_sizes])

# 3. Анализируем и строим график


        results_df = analyze_window_size_effect(valid_data, window_sizes, cond_dir)

        data_csv_file.extend([results_df])
            # Create a csv.writer object
        # Open the file in write mode

        print(results_df)
    plt.show()
csv_file_path = 'result_diki_fuller_test.csv'
with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    # Write data to the CSV file
    zip(*data_csv_file)
    writer.writerows(data_csv_file)
# Пример с реальным временным рядом (например, загрузка из CSV)
# df = pd.read_csv('your_time_series_data.csv', index_col='Date', parse_dates=True) # Пример загрузки
# time_series = df['YourColumn']
# plot_dickey_fuller(time_series)


# Пример с дифференцированным временным рядом (если исходный ряд нестационарен)
# diff_time_series = time_series.diff().dropna() # Берем первую разность
# plot_dickey_fuller(diff_time_series)
