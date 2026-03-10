import logging

import numpy as np
import pandas as pd
from scipy.ndimage import uniform_filter1d

from stepanalyzer.Algorithms.KinematicsFun import local_extrema_windowed
from stepanalyzer.Algorithms.StepCycleDetector import StepCycleDetector

PAW_INDICES = [1, 2, 4, 5, 7, 8, 10, 11]  # Индексы точек для лап
PAW_LABELS = ['Left front paw', 'Right front paw', 'Left hind paw', 'Left knee',
              'Right hind paw', 'Right knee']
PAW_COLORS = np.array([
    [0, 0.4470, 0.7410],
    [0.3010, 0.7450, 0.9330],
    [0.8500, 0.3250, 0.0980],
    [0.9290, 0.6940, 0.1250],
    [0.4940, 0.1840, 0.5560],
    [0.8310, 0.4310, 0.6120]
])
METRICS_PER_PAW = 8  # 4 для stride time + 4 для stride interval
N_PAWS = 6

METRICS = ['Median stride time', 'Mean stride time', 'Kvar stride time', 'Frac stride time',
           'Median stride intl', 'Mean stride intl', 'Kvar stride intl', 'Frac stride intl']


def try_read_csv_with_separators(filepath):
    """Попытка прочитать CSV с ',' или ';' как разделителем."""
    try:
        with open(filepath, 'r') as f:
            return pd.read_csv(f, sep=',', header=None).values
    except:
        with open(filepath, 'r') as f:
            return pd.read_csv(f, sep=';', header=None).values


def compute_paw_speed(x_coords, y_coords, smoothing_window=5):
    """Вычисляет сглаженную скорость по координатам лапы."""
    x = np.asarray(x_coords, dtype=float)
    y = np.asarray(y_coords, dtype=float)

    dx = np.gradient(x[1:])
    dy = np.gradient(y[1:])
    speed = np.sqrt(dx ** 2 + dy ** 2)
    return uniform_filter1d(speed, size=smoothing_window)


def calculate_step_result(config, axs, check_auto):
    stat_tabl = np.full((len(METRICS) * 6), np.nan)
    try:

        tbl = try_read_csv_with_separators(config.name_csv_file)
        logging.INFO(f"Размер данных: {tbl.shape}")

        # Проверяем, есть ли достаточно столбцов
        if tbl.shape[1] < 2:
            logging.ERROR(f"В файле {config.name_csv_file} недостаточно столбцов. Пропускаем.")

        # Берем все столбцы, начиная со второго
        data_animal = tbl[:, 1:]
        n_rows, n_cols = data_animal.shape

        # Определяем количество точек (лап) - должно быть кратно 3 (x, y, likelihood)
        n_points = n_cols // 3
        if n_points < 4:
            logging.ERROR(f"Недостаточно данных для 4 лап в файле {config.name_csv_file}. Пропускаем.")

        try:
            # Reshape и transpose как в MATLAB
            data_animal = data_animal.reshape(n_rows, n_points, 3)
            data_animal = data_animal[:, :, :2]  # Берем только x и y, игнорируем likelihood
        except Exception as e:
            logging.ERROR(f"Ошибка при переформатировании данных: {e}")

        # Визуализация временных рядов скорости
        Np = 6
        caps = ['Left front paw', 'Right front paw', 'Left hind paw', 'Left knee', 'Right hind paw', 'Right knee']

        X_raw = [None] * Np

        for p in range(Np):
            if PAW_INDICES[p] >= data_animal.shape[1]:
                logging.WARNING(f"Индекс лапы {PAW_INDICES[p]} выходит за пределы данных. Пропускаем.")
                continue

            x = data_animal[:, PAW_INDICES[p], 0]
            y = data_animal[:, PAW_INDICES[p], 1]
            dx = np.gradient(np.array(x[1:], dtype=float))
            dy = np.gradient(np.array(y[1:], dtype=float))
            speed = np.sqrt(dx ** 2 + dy ** 2)
            X_raw[p] = uniform_filter1d(speed, size=5)
            axs[p].plot(X_raw[p], color=PAW_COLORS[p], linewidth=2)
            axs[p].set_ylabel(caps[p])
            axs[p].grid(True)

        if check_auto:
            grad_X, T, im, X_sel, band_span, band_intl = auto_calculate_result(Np, X_raw)
            for n in range(Np):
                if X_raw[n] is None:
                    continue
                axs[n].plot(grad_X, color='#7E2F8E', alpha=0.7)
                axs[n].axhline(0, color='k', linestyle='--', alpha=0.5)
                axs[n].axhline(T[im[n]][n], color='g', alpha=0.7)
                axs[n].axhline(-T[im[n]][n], color='g', alpha=0.7)

                # Отображаем только выбранные интервалы
                if X_sel[im[n]][n] is not None:
                    sel_mask = X_sel[im[n]][n].astype(float)
                    sel_mask[sel_mask == 0] = np.nan
                    max_val = np.nanmax(X_raw[n]) if len(X_raw[n]) > 0 else 1
                    axs[n].plot(sel_mask * max_val * 0.9, 'k-', linewidth=2)

                # Расчет статистических метрик
            for n in range(Np):
                if band_span[im[n]][n] is None or len(band_span[im[n]][n]) == 0:
                    continue
                span_data = band_span[im[n]][n]
                intl_data = band_intl[im[n]][n]
                sel_data = X_sel[im[n]][n]

                if len(span_data) > 0:
                    stat_tabl[n * 8] = np.median(span_data)
                    stat_tabl[n * 8 + 1] = np.mean(span_data)
                    stat_tabl[n * 8 + 2] = np.std(span_data) / np.mean(span_data) if np.mean(
                        span_data) != 0 else np.nan
                    stat_tabl[n * 8 + 3] = np.sum(sel_data) / len(sel_data) if len(sel_data) > 0 else np.nan

                if len(intl_data) > 0:
                    stat_tabl[n * 8 + 4] = np.median(intl_data)
                    stat_tabl[n * 8 + 5] = np.mean(intl_data)
                    stat_tabl[n * 8 + 6] = np.std(intl_data) / np.mean(intl_data) if np.mean(
                        intl_data) != 0 else np.nan
                    stat_tabl[n * 8 + 7] = np.sum(~sel_data) / len(sel_data) if len(sel_data) > 0 else np.nan
        else:
            stat_tabl = []
            stepCycleDetector = StepCycleDetector(config=config)
            for i in range(0, 6):
                result_analyze, __ = stepCycleDetector.detect_step_cycles(X_raw[i],
                                                                          local_extrema_windowed(X_raw[i]),
                                                                          local_extrema_windowed(X_raw[i], mode="min"))
                axs[i].plot(result_analyze, color='green')
                #stat_tabl.extend(analyze_step_parameters(result_analyze))
    except Exception as e:
        print(f"Ошибка при обработке файла {config.name_csv_file}: {e}")

    return stat_tabl

    # if self.results_df is not None:
    #     self.results_df.pd.concat([self.results_df, pd.DataFrame(stat_tabl)],  ignore_index=True)
    # else:
    #     self.results_df = pd.DataFrame(stat_tabl)


def auto_calculate_result(N_PAWS, X_raw):
    M = np.arange(0.5, 1.1, 0.1)
    lm = len(M)
    X_sel = [[None] * N_PAWS for _ in range(lm)]
    T = [[None] * N_PAWS for _ in range(lm)]
    band_init = [[None] * N_PAWS for _ in range(lm)]
    band_term = [[None] * N_PAWS for _ in range(lm)]
    band_span = [[None] * N_PAWS for _ in range(lm)]
    band_intl = [[None] * N_PAWS for _ in range(lm)]
    std_span = np.full((lm, N_PAWS), np.nan)
    std_intl = np.full((lm, N_PAWS), np.nan)
    grad_X = None

    for n in range(N_PAWS):
        if X_raw[n] is None:
            continue
        grad_X = np.gradient(X_raw[n]) * X_raw[n]
        grad_X = uniform_filter1d(grad_X, size=5)
        S_X = np.nanstd(grad_X)
        if S_X == 0:  # Избегаем деления на ноль
            S_X = 1e-10
        grad_X = grad_X / S_X

        for m in range(lm):
            T_val = np.nanstd(grad_X) * M[m]
            T[m][n] = T_val

            # Поиск положительных пиков
            pos_mask = grad_X > T_val
            pos_diff = np.diff(pos_mask.astype(int))
            X_pos_init = np.where(pos_diff > 0)[0] + 1
            X_pos_term = np.where(pos_diff < 0)[0] + 1

            D_pos = np.zeros_like(grad_X, dtype=bool)
            if len(X_pos_term) > 0 and len(X_pos_init) > 0:
                if X_pos_term[0] < X_pos_init[0]:
                    X_pos_term = X_pos_term[1:]
                nt = min(len(X_pos_init), len(X_pos_term))
                if nt > 0:
                    X_pos_init = X_pos_init[:nt]
                    X_pos_term = X_pos_term[:nt]
                    for j in range(nt):
                        if X_pos_init[j] < X_pos_term[j]:
                            segment = grad_X[X_pos_init[j]:X_pos_term[j]]
                            idx_max = np.argmax(segment)
                            D_pos[X_pos_init[j] + idx_max] = True

            # Поиск отрицательных пиков
            neg_mask = grad_X < -T_val
            neg_diff = np.diff(neg_mask.astype(int))
            X_neg_init = np.where(neg_diff > 0)[0] + 1
            X_neg_term = np.where(neg_diff < 0)[0] + 1

            D_neg = np.zeros_like(grad_X, dtype=bool)
            if len(X_neg_term) > 0 and len(X_neg_init) > 0:
                if X_neg_term[0] < X_neg_init[0]:
                    X_neg_term = X_neg_term[1:]
                nt_neg = min(len(X_neg_init), len(X_neg_term))
                if nt_neg > 0:
                    X_neg_init = X_neg_init[:nt_neg]
                    X_neg_term = X_neg_term[:nt_neg]
                    for j in range(nt_neg):
                        if X_neg_init[j] < X_neg_term[j]:
                            segment = grad_X[X_neg_init[j]:X_neg_term[j]]
                            idx_min = np.argmin(segment)
                            D_neg[X_neg_init[j] + idx_min] = True

            # Формирование интервалов движения
            S1 = len(grad_X)
            X_sel_current = np.zeros(S1, dtype=bool)
            band_init_current = []
            band_term_current = []

            t = -1  # счетчик интервалов
            for i in range(1, S1 - 1):
                if t < 0 or not X_sel_current[i - 1]:
                    if i < len(D_pos) and D_pos[i]:
                        X_sel_current[i] = True
                        t += 1
                        band_init_current.append(i)
                else:
                    if not (i < len(D_neg) and D_neg[i]):
                        X_sel_current[i] = True
                    else:
                        if t < len(band_term_current):
                            band_term_current[t] = i
                        else:
                            band_term_current.append(i)

            # Проверка согласованности интервалов
            if len(band_init_current) > len(band_term_current):
                if len(band_init_current) > 0:
                    X_sel_current[band_init_current[-1]:] = False
                    band_init_current = band_init_current[:-1]

            # Сохранение результатов
            if len(band_init_current) > 0 and len(band_term_current) > 0:
                if len(band_init_current) == len(band_term_current):
                    band_span_current = np.array(band_term_current) - np.array(band_init_current)
                    std_span_val = np.std(band_span_current) / len(band_span_current) if len(
                        band_span_current) > 0 else np.nan

                    if len(band_init_current) > 1:
                        band_intl_current = np.diff(band_init_current)
                        std_intl_val = np.std(band_intl_current) / len(band_intl_current) if len(
                            band_intl_current) > 0 else np.nan
                    else:
                        band_intl_current = np.array([])
                        std_intl_val = np.nan
                else:
                    band_span_current = np.array([])
                    band_intl_current = np.array([])
                    std_span_val = np.nan
                    std_intl_val = np.nan
            else:
                band_span_current = np.array([])
                band_intl_current = np.array([])
                std_span_val = np.nan
                std_intl_val = np.nan

            X_sel[m][n] = X_sel_current
            band_init[m][n] = band_init_current
            band_term[m][n] = band_term_current
            band_span[m][n] = band_span_current
            band_intl[m][n] = band_intl_current
            std_span[m, n] = std_span_val
            std_intl[m, n] = std_intl_val

    # Выбор оптимальных параметров для передних и задних лап
    front_ratios = np.zeros(lm)
    hind_ratios = np.zeros(lm)

    for m in range(lm):
        front_vals = []
        hind_vals = []

        for n in range(2):  # Передние лапы
            if not np.isnan(std_span[m, n]) and not np.isnan(std_intl[m, n]) and std_intl[m, n] != 0:
                front_vals.append(std_span[m, n] / std_intl[m, n])

        for n in range(2, 4):  # Задние лапы
            if not np.isnan(std_span[m, n]) and not np.isnan(std_intl[m, n]) and std_intl[m, n] != 0:
                hind_vals.append(std_span[m, n] / std_intl[m, n])

        front_ratios[m] = np.mean(front_vals) if len(front_vals) > 0 else np.nan
        hind_ratios[m] = np.mean(hind_vals) if len(hind_vals) > 0 else np.nan

    # Находим оптимальные индексы
    if not np.all(np.isnan(front_ratios)):
        im_front = np.nanargmin(front_ratios)
    else:
        im_front = 0

    if not np.all(np.isnan(hind_ratios)):
        im_hind = np.nanargmin(hind_ratios)
    else:
        im_hind = 0

    im = [im_front, im_front, im_hind, im_hind]
    return grad_X, T, im, X_sel, band_span, band_intl

# if __name__ == "__main__":
#     main()
