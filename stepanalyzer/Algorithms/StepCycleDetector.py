import numpy as np


class StepCycleDetector:
    def __init__(self, config):
        self.speed_change_min = config.speed_change_min.value()
        self.speed_change_max = config.speed_change_max.value()
        self.travel_time_min = config.travel_time_min.value()
        self.travel_time_max = config.travel_time_max.value()
        self.amplitude_offset = 100  # вместо "magic number" 100

    def preprocess_peaks(self, data, peaks_max, peaks_min, window_size=3):
        """Предобработка пиков для удаления шума"""
        # Фильтрация слишком близких пиков
        filtered_max = self._filter_close_peaks(peaks_max, window_size)
        filtered_min = self._filter_close_peaks(peaks_min, window_size)

        # Удаление пиков с малой амплитудой
        filtered_max = [p for p in filtered_max
                        if self._has_sufficient_amplitude(data, p, filtered_min)]

        return filtered_max, filtered_min

    def _filter_close_peaks(self, peaks, min_distance):
        """Удаление слишком близких пиков"""
        if not peaks:
            return []

        filtered = [peaks[0]]
        for peak in peaks[1:]:
            if peak - filtered[-1] >= min_distance:
                filtered.append(peak)
        return filtered

    def get_cycle_statistics(self, data, cycles):
        """Получение статистики по найденным циклам"""
        if not cycles:
            return {}

        stats = {
            'total_cycles': len(cycles),
            'avg_amplitude': 0,
            'avg_duration': 0,
            'avg_rise_time': 0,
            'avg_fall_time': 0,
            'valid_cycles': [],
            'invalid_cycles': []
        }

        amplitudes = []
        durations = []
        rise_times = []
        fall_times = []

        for start_min, max_point, end_min in cycles:
            amplitude = abs(data[max_point] - data[start_min])
            duration = end_min - start_min
            rise_time = max_point - start_min
            fall_time = end_min - max_point

            amplitudes.append(amplitude)
            durations.append(duration)
            rise_times.append(rise_time)
            fall_times.append(fall_time)

            # Проверка на выбросы
            if (self.speed_change_min < amplitude < self.speed_change_max and
                    self.travel_time_min < duration < self.travel_time_max):
                stats['valid_cycles'].append((start_min, max_point, end_min))
            else:
                stats['invalid_cycles'].append((start_min, max_point, end_min))

        # Средние значения
        if amplitudes:
            stats['avg_amplitude'] = np.mean(amplitudes)
            stats['avg_duration'] = np.mean(durations)
            stats['avg_rise_time'] = np.mean(rise_times)
            stats['avg_fall_time'] = np.mean(fall_times)
            stats['amplitude_std'] = np.std(amplitudes)
            stats['duration_std'] = np.std(durations)

        return stats

    def _visualize_cycles(self, data, cycles):
        """Визуализация найденных циклов"""
        result = np.zeros_like(data, dtype=float)

        for i, (start_min, max_point, end_min) in enumerate(cycles):
            # Проверяем границы
            if end_min >= len(data):
                continue

            # Можно использовать разные стратегии заполнения:
            # 1. Постоянное значение
            # result[start_min:end_min+1] = data[max_point] + self.amplitude_offset

            # 2. Линейная интерполяция
            self._fill_with_interpolation(result, data, start_min, max_point, end_min, i)

            # 3. Гауссово распределение
            # self._fill_with_gaussian(result, data, start_min, max_point, end_min, i)

        return result

    def _fill_with_interpolation(self, result, data, start_min, max_point, end_min, cycle_num):
        """Заполнение с линейной интерполяцией"""
        # Подъем
        for j in range(start_min, max_point + 1):
            t = (j - start_min) / (max_point - start_min)
            result[j] = data[start_min] + t * (data[max_point] - data[start_min])

        # Спуск
        for j in range(max_point, end_min + 1):
            t = (j - max_point) / (end_min - max_point)
            result[j] = data[max_point] + t * (data[end_min] - data[max_point])

    def _fill_with_gaussian(self, result, data, start_min, max_point, end_min, cycle_num):
        """Заполнение гауссовой кривой"""
        cycle_length = end_min - start_min
        x = np.linspace(-3, 3, cycle_length + 1)
        gaussian = np.exp(-x ** 2 / 2)
        gaussian = gaussian * (data[max_point] - data[start_min]) + data[start_min]

        for j in range(start_min, end_min + 1):
            if j - start_min < len(gaussian):
                result[j] = gaussian[j - start_min]

    def _validate_maximum(self, data, start_min_idx, max_idx):
        """Проверка валидности максимума"""
        if start_min_idx >= max_idx:
            return False

        # Проверка амплитуды (разница значений)
        amplitude = abs(data[max_idx] - data[start_min_idx])

        # Проверка времени подъема
        rise_time = max_idx - start_min_idx

        return (self.speed_change_min < amplitude < self.speed_change_max and
                self.travel_time_min < rise_time < self.travel_time_max)

    def _validate_cycle_completion(self, data, current_cycle, end_min_idx):
        """Проверка завершения цикла"""
        if len(current_cycle) != 2:  # Должны быть минимум и максимум
            return False

        start_min_idx, max_idx = current_cycle

        # Проверка времени полного цикла
        full_cycle_time = end_min_idx - start_min_idx

        # Проверка симметрии цикла (опционально)
        if not self._check_cycle_symmetry(data, start_min_idx, max_idx, end_min_idx):
            return False

        return self.travel_time_min < full_cycle_time < self.travel_time_max

    def _check_cycle_symmetry(self, data, start_min, max_point, end_min):
        """Проверка симметрии цикла (опциональная)"""
        # Можно добавить проверку на схожесть формы
        rise_time = max_point - start_min
        fall_time = end_min - max_point

        # Разница между подъемом и спуском не должна быть слишком большой
        time_ratio = abs(rise_time - fall_time) / min(rise_time, fall_time)
        return time_ratio < 0.5  # Максимум 50% разницы

    def detect_step_cycles(self, data_init, peaks_max, peaks_min):
        """Основной метод детекции шаговых циклов"""
        # Объединяем и сортируем все пики
        all_peaks = sorted(peaks_max + peaks_min)

        # Машина состояний для поиска циклов
        cycles = self._find_valid_cycles(data_init, all_peaks, peaks_max, peaks_min)

        # Визуализируем найденные циклы
        result = self._visualize_cycles(data_init, cycles)

        return result, cycles

    def _find_valid_cycles(self, data_init, all_peaks, peaks_max, peaks_min):
        """Поиск валидных циклов"""
        cycles = []
        current_cycle = []
        state = 'WAITING_FOR_START_MIN'

        for peak_idx in all_peaks:
            if state == 'WAITING_FOR_START_MIN' and peak_idx in peaks_min:
                # Начало нового цикла
                current_cycle = [peak_idx]
                state = 'WAITING_FOR_MAX'

            elif state == 'WAITING_FOR_MAX' and peak_idx in peaks_max:
                if self._validate_maximum(data_init, current_cycle[0], peak_idx):
                    current_cycle.append(peak_idx)
                    state = 'WAITING_FOR_END_MIN'
                else:
                    # Сброс невалидного цикла
                    current_cycle = []
                    state = 'WAITING_FOR_START_MIN'

            elif state == 'WAITING_FOR_END_MIN' and peak_idx in peaks_min:
                if self._validate_cycle_completion(data_init, current_cycle, peak_idx):
                    current_cycle.append(peak_idx)
                    cycles.append(tuple(current_cycle))
                    current_cycle = []
                    state = 'WAITING_FOR_START_MIN'
                else:
                    # Неполный цикл - сброс
                    current_cycle = []
                    state = 'WAITING_FOR_START_MIN'

        return cycles