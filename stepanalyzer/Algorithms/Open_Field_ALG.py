from statistics import median, mean

import numpy as np
import pandas as pd
from scipy.ndimage import uniform_filter1d

from stepanalyzer.Algorithms.KinematicsFun import local_extrema_windowed


def main():
    # Чтение списка файлов
    try:
        with open('D:\\Diplom\\DiplomPy\\data\\open_field\\files_data_openfield_clean.lst', 'r') as f:
            animals = f.read().splitlines()
    except FileNotFoundError:
        print("Файл 'files_data_openfield_clean.lst' не найден.")
        return

    Na = len(animals) - 1
    if Na <= 0:
        print("Нет данных для обработки.")
        return

    data = [None] * Na
    Thr_likelihood = 0.05

    metrics = ['Median stride time', 'Mean stride time', 'Kvar stride time', 'Frac stride time',
               'Median stride intl', 'Mean stride intl', 'Kvar stride intl', 'Frac stride intl']
    stat_tabl = np.full((Na, len(metrics) * 4), np.nan)

    for animal in range(Na):
        # Чтение и обработка данных
        try:
            # Пробуем разные разделители
            try:
                tbl = pd.read_csv(animals[animal], sep=',', header=None).values
            except:
                tbl = pd.read_csv(animals[animal], sep=',', header=None).values

            print(f"Размер данных: {tbl.shape}")

            # Проверяем, есть ли достаточно столбцов
            if tbl.shape[1] < 2:
                print(f"В файле {animals[animal]} недостаточно столбцов. Пропускаем.")
                continue

            # Берем все столбцы, начиная со второго (аналогично MATLAB's tbl(:,2:end))
            data_animal = tbl[:, 1:]
            n_rows, n_cols = data_animal.shape

            # Определяем количество точек (лап) - должно быть кратно 3 (x, y, likelihood)
            n_points = n_cols // 3
            if n_points < 4:
                print(f"Недостаточно данных для 4 лап в файле {animals[animal]}. Пропускаем.")
                continue

            print(f"В файле {animals[animal]} ")
            # Переформатирование данных аналогично MATLAB-коду
            try:
                # Reshape и transpose как в MATLAB
                data_animal = data_animal.reshape(n_rows, 3, n_points)
                data_animal = np.transpose(data_animal, (0, 2, 1))
                data_animal = data_animal[:, :, :2]  # Берем только x и y, игнорируем likelihood
            except Exception as e:
                print(f"Ошибка при переформатировании данных: {e}")
                continue

            print(f"{animals[animal]} → {data_animal.shape}")

            # Визуализация временных рядов скорости
            Np = 4
            # Индексы для лап (0-based)
            Npts = [1, 2, 4, 5]  # Левая передняя, правая передняя, левая задняя, правая задняя
            caps = ['Left front paw', 'Right front paw', 'Left hind paw', 'Right hind paw']
            TypeColor = np.array([[0, 0.4470, 0.7410], [0.3010, 0.7450, 0.9330],
                                  [0.8500, 0.3250, 0.0980], [1, 0, 0]])

            X_raw = [None] * Np

            for p in range(Np):
                if Npts[p] >= data_animal.shape[1]:
                    print(f"Индекс лапы {Npts[p]} выходит за пределы данных. Пропускаем.")
                    continue

                x = data_animal[:, Npts[p], 0]
                y = data_animal[:, Npts[p], 1]
                print(np.array(x[1:]))
                dx = np.gradient(np.array(x[1:], dtype=float))
                dy = np.gradient(np.array(y[1:], dtype=float))
                speed = np.sqrt(dx ** 2 + dy ** 2)
                X_raw[p] = uniform_filter1d(speed, size=5)

            # Расчет градиента
            M = np.arange(0.5, 1.1, 0.1)
            lm = len(M)
            X_sel = [[None] * Np for _ in range(lm)]
            T = [[None] * Np for _ in range(lm)]
            band_init = [[None] * Np for _ in range(lm)]
            band_term = [[None] * Np for _ in range(lm)]
            band_span = [[None] * Np for _ in range(lm)]
            std_span = np.full((lm, Np), np.nan)
            band_intl = [[None] * Np for _ in range(lm)]
            std_intl = np.full((lm, Np), np.nan)

            for n in range(Np):
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

            # Визуализация результатов
            for n in range(Np):
                if X_raw[n] is None:
                    continue


                # Отображаем только выбранные интервалы
                if X_sel[im[n]][n] is not None:
                    sel_mask = X_sel[im[n]][n].astype(float)
                    sel_mask[sel_mask == 0] = np.nan
                    max_val = np.nanmax(X_raw[n]) if len(X_raw[n]) > 0 else 1

            # Расчет статистических метрик
            for n in range(Np):
                if band_span[im[n]][n] is None or len(band_span[im[n]][n]) == 0:
                    continue

                span_data = band_span[im[n]][n]
                intl_data = band_intl[im[n]][n]
                sel_data = X_sel[im[n]][n]

                if len(span_data) > 0:
                    stat_tabl[animal, n * 8] = np.median(span_data)
                    stat_tabl[animal, n * 8 + 1] = np.mean(span_data)
                    stat_tabl[animal, n * 8 + 2] = np.std(span_data) / np.mean(span_data) if np.mean(
                        span_data) != 0 else np.nan
                    stat_tabl[animal, n * 8 + 3] = np.sum(sel_data) / len(sel_data) if len(sel_data) > 0 else np.nan

                if len(intl_data) > 0:
                    stat_tabl[animal, n * 8 + 4] = np.median(intl_data)
                    stat_tabl[animal, n * 8 + 5] = np.mean(intl_data)
                    stat_tabl[animal, n * 8 + 6] = np.std(intl_data) / np.mean(intl_data) if np.mean(
                        intl_data) != 0 else np.nan
                    stat_tabl[animal, n * 8 + 7] = np.sum(~sel_data) / len(sel_data) if len(sel_data) > 0 else np.nan
            # plt.show()

        except Exception as e:
            print(f"Ошибка при обработке файла {animals[animal]}: {e}")
            continue

    # Сохранение результатов
    try:
        results_df = pd.DataFrame(stat_tabl)
        metric_columns = []
        for i in range(4):  # Для каждой лапы
            for metric in metrics:
                metric_columns.append(f'Paw_{i + 1}_{metric}')

        results_df.columns = metric_columns
        results_df.to_csv('movement_analysis_results.csv', index=False)
        print("Анализ завершен. Результаты сохранены в movement_analysis_results.csv")
    except Exception as e:
        print(f"Ошибка при сохранении результатов: {e}")


def calculate_step_result(self, axs, check_auto):
    metrics = ['Median stride time', 'Mean stride time', 'Kvar stride time', 'Frac stride time',
               'Median stride intl', 'Mean stride intl', 'Kvar stride intl', 'Frac stride intl']
    stat_tabl = np.full((len(metrics) * 4), np.nan)
    try:
        try:
            with open(self.name_csv_file, 'r') as f:
                tbl = pd.read_csv(f, sep=',', header=None).values
        except:
            with open(self.name_csv_file, 'r') as f:
                tbl = pd.read_csv(f, sep=';', header=None).values

        print(f"Размер данных: {tbl.shape}")

        # Проверяем, есть ли достаточно столбцов
        if tbl.shape[1] < 2:
            print(f"В файле {self.name_csv_file} недостаточно столбцов. Пропускаем.")

        # Берем все столбцы, начиная со второго
        data_animal = tbl[:, 1:]
        n_rows, n_cols = data_animal.shape

        # Определяем количество точек (лап) - должно быть кратно 3 (x, y, likelihood)
        n_points = n_cols // 3
        if n_points < 4:
            print(f"Недостаточно данных для 4 лап в файле {self.name_csv_file}. Пропускаем.")

        try:
            # Reshape и transpose как в MATLAB
            data_animal = data_animal.reshape(n_rows, 3, n_points)
            data_animal = np.transpose(data_animal, (0, 2, 1))
            data_animal = data_animal[:, :, :2]  # Берем только x и y, игнорируем likelihood
        except Exception as e:
            print(f"Ошибка при переформатировании данных: {e}")

        # Визуализация временных рядов скорости
        Np = 4
        # Индексы для лап (0-based)
        Npts = [1, 2, 4, 5]  # Левая передняя, правая передняя, левая задняя, правая задняя
        caps = ['Left front paw', 'Right front paw', 'Left hind paw', 'Right hind paw']
        TypeColor = np.array([[0, 0.4470, 0.7410], [0.3010, 0.7450, 0.9330],
                              [0.8500, 0.3250, 0.0980], [1, 0, 0]])
        X_raw = [None] * Np

        for p in range(Np):
            if Npts[p] >= data_animal.shape[1]:
                print(f"Индекс лапы {Npts[p]} выходит за пределы данных. Пропускаем.")
                continue

            x = data_animal[:, Npts[p], 0]
            y = data_animal[:, Npts[p], 1]
            dx = np.gradient(np.array(x[1:], dtype=float))
            dy = np.gradient(np.array(y[1:], dtype=float))
            speed = np.sqrt(dx ** 2 + dy ** 2)
            X_raw[p] = uniform_filter1d(speed, size=5)
            axs[p].plot(X_raw[p], color=TypeColor[p], linewidth=2)
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
            for i in range(0, 4):
                result_analyze = manual_calculate_result(self, X_raw[i])
                axs[i].plot(result_analyze, color='green')
                stat_tabl.extend(analyze_step_parameters(result_analyze))
    except Exception as e:
        print(f"Ошибка при обработке файла {self.name_csv_file}: {e}")

    return stat_tabl

    # if self.results_df is not None:
    #     self.results_df.pd.concat([self.results_df, pd.DataFrame(stat_tabl)],  ignore_index=True)
    # else:
    #     self.results_df = pd.DataFrame(stat_tabl)


def auto_calculate_result(Np, X_raw):
    M = np.arange(0.5, 1.1, 0.1)
    lm = len(M)
    X_sel = [[None] * Np for _ in range(lm)]
    T = [[None] * Np for _ in range(lm)]
    band_init = [[None] * Np for _ in range(lm)]
    band_term = [[None] * Np for _ in range(lm)]
    band_span = [[None] * Np for _ in range(lm)]
    band_intl = [[None] * Np for _ in range(lm)]
    std_span = np.full((lm, Np), np.nan)
    std_intl = np.full((lm, Np), np.nan)
    grad_X = None

    for n in range(Np):
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


def manual_calculate_result(self, data_init):
    """Form a complex number.
       @:param local_data - array with angels
       @re
       """
    peaks_max = local_extrema_windowed(data_init)

    peaks_min = local_extrema_windowed(data_init, mode="min")

    temp_peaks_result = []
    peaks_list = []
    peaks_list.extend(peaks_max)
    peaks_list.extend(peaks_min)
    peaks_list.sort()
    prev_max = False
    start_step = False

    for i in range(0, len(peaks_list)):
        if peaks_list[i] in peaks_min and not prev_max and not start_step:
            temp_peaks_result.append(peaks_list[i])
            prev_max = False
            start_step = True
        elif (peaks_list[i] in peaks_max and start_step
              and abs(temp_peaks_result[-1] - peaks_list[i]) < self.speed_change.value()):
            temp_peaks_result.append(peaks_list[i])
            prev_max = True
        elif peaks_list[i] in peaks_min and prev_max:
            if abs(temp_peaks_result[-2] - peaks_list[i]) > self.travel_time_min.value() and abs(
                    temp_peaks_result[-2] - peaks_list[i]) < self.travel_time_max.value():
                temp_peaks_result.append(peaks_list[i])
                start_step = False
                prev_max = False
            else:
                temp_peaks_result.pop()
                temp_peaks_result.pop()
                temp_peaks_result.append(peaks_list[i])
                prev_max = False
                start_step = True

    temp_result = np.zeros(len(data_init))
    for i in range(0, len(temp_peaks_result) - 2, 3):
        for j in range(temp_peaks_result[i], temp_peaks_result[i + 2] + 1):
            temp_result[j] = data_init[temp_peaks_result[i + 1]] + 100
    return temp_result


def analyze_step_parameters(step_data):
    data = np.array(step_data)
    steps = []
    none_steps = []
    stat_tbl = []
    time = 0
    none_step_time = 0
    for i in range(0, len(data)):
        if data[i] != 0.0:
            time += 1
        elif time != 0 and data[i] == 0.0:
            steps.append(time)
            time = 0
        if data[i] == 0.0:
            none_step_time += 1
        elif none_step_time != 0 and data[i] != 0.0:
            none_steps.append(none_step_time)

    stat_tbl.append(median(steps))
    stat_tbl.append(mean(steps))
    stat_tbl.append(np.std(steps) / np.mean(steps) if np.mean(steps) != 0 else np.nan)
    stat_tbl.append(np.sum(steps) / len(steps) if len(steps) > 0 else np.nan)

    stat_tbl.append(median(none_steps))
    stat_tbl.append(mean(none_steps))
    stat_tbl.append(np.std(none_steps) / np.mean(none_steps) if np.mean(none_steps) != 0 else np.nan)
    stat_tbl.append(np.sum(none_steps) / len(none_steps) if len(none_steps) > 0 else np.nan)

    return stat_tbl

if __name__ =="__main__":
    main()
