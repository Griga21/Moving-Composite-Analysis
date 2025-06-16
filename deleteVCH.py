import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

# Генерация данных с выбросами
np.random.seed(42)
x = np.linspace(0, 10, 100)
y = np.sin(x) + np.random.normal(0, 0.2, size=x.shape)

# Добавим выбросы в данные
y_with_outliers = y.copy()
y_with_outliers[::10] += np.random.normal(3, 1, size=10)  # выбросы через каждые 10 точек

# Функция для удаления выбросов с помощью IQR
def remove_outliers_iqr(y):
    q1 = np.percentile(y, 25)
    q3 = np.percentile(y, 75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    y_filtered = y.copy()
    mask = (y < lower_bound) | (y > upper_bound)
    y_filtered[mask] = np.nan  # выбросы заменим на NaN
    return y_filtered

# Удаление выбросов
y_clean = remove_outliers_iqr(y_with_outliers)

# Сглаживание и замена NaN средним значением для визуализации
y_clean_filled = np.where(np.isnan(y_clean), np.nanmean(y_clean), y_clean)

# Построение графиков
plt.figure(figsize=(10, 6))

plt.plot(x, gaussian_filter1d(y_with_outliers, sigma=1), label='С выбросами', color='red', linewidth = 5)
plt.plot(x, gaussian_filter1d(y_clean_filled, sigma=1), label='Без выбросов (IQR)', color='green', linewidth = 5)
plt.xlabel('Кадры', size = 20)
plt.ylabel('Сгибание/Разгибание сустава (градусы)', size = 20)
plt.title('Среднее скользящие окно',size = 20)
plt.title('График с выбросами и без них', size = 20)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()