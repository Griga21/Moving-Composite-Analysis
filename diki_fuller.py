import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.patches as mpatches

# Загружаем данные
file_path =  r'C:\Users\griga\Downloads\Telegram Desktop\Result_added_.xlsx'
df = pd.read_excel(file_path, sheet_name='Data', header=1)

# Переименовываем первые столбцы для удобства
column_names = ['Index', 'Rehab', 'Day', 'Number Rat', 'Step Params', 'Angle Params',
                'Average Max Angel', 'Average Min Angel', 'Average Step Duration (s)',
                'Total Count Step', 'Average height Step'] + list(df.columns[11:])
df.columns = column_names[:len(df.columns)]


# Создаем колонку с объединенными днями (3 и 7 вместе)
def combine_days(day):
    if day in [3, 7]:
        return '3+7'
    else:
        return str(day)


df['Day_combined'] = df['Day'].apply(combine_days)

# Выбираем нужные колонки
columns_to_plot = ['Total Count Step', 'Average Max Angel', 'Average Min Angel',
                   'Average Step Duration (s)', 'Average height Step']

# Очищаем данные от пропусков
df_clean = df.copy()
for col in columns_to_plot:
    df_clean = df_clean[pd.to_numeric(df_clean[col], errors='coerce').notna()]

# Преобразуем колонки в числовой формат
for col in columns_to_plot:
    df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

# Удаляем строки с NaN в ключевых колонках
df_clean = df_clean.dropna(subset=['Day_combined', 'Rehab'] + columns_to_plot)

# Преобразуем Rehab в строку для лучшей визуализации
df_clean['Rehab'] = df_clean['Rehab'].astype(str)

# Получаем уникальные дни в правильном порядке
unique_days = ['0', '3+7', '11', '14', '18', '21', '25', '28']
# Фильтруем только те дни, которые есть в данных
available_days = [day for day in unique_days if day in df_clean['Day_combined'].unique()]
df_clean = df_clean[df_clean['Day_combined'].isin(available_days)]

# Настраиваем стиль
sns.set_style("whitegrid")
# Цвета для Rehab
rehab_colors = {'0': '#FF8C42',  # Оранжевый для SCI
                '1': '#2E8B57'}  # Зеленый для SCI_TMT


# Функция для создания графика с выделенным Day 0
def create_boxplot_with_highlight(data, x, y, title, ylabel, fig_num):
    plt.figure(fig_num, figsize=(14, 8))

    # Создаем список цветов для каждого дня и группы Rehab
    days = data[x].unique()
    days_sorted = sorted(days, key=lambda d: available_days.index(d) if d in available_days else len(available_days))

    # Получаем позиции на оси X
    x_positions = []
    x_labels = []

    # Создаем boxplot для каждого дня отдельно, чтобы контролировать цвета
    for i, day in enumerate(days_sorted):
        day_data = data[data[x] == day]

        # Для Day 0 используем синий цвет, для остальных - стандартные цвета
        if day == '0':
            # Для Day 0 используем синий цвет для обеих групп
            box_colors = ['#1E88E5', '#1E88E5']  # Синий для Day 0
        else:
            # Для остальных дней используем стандартные цвета
            box_colors = [rehab_colors['0'], rehab_colors['1']]

        # Создаем boxplot для текущего дня
        bp = sns.boxplot(data=day_data, x=x, y=y, hue='Rehab',
                         palette=box_colors, showfliers=False,
                         order=[day], ax=plt.gca())

    # Настраиваем заголовок и подписи
    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Day', fontsize=14, fontweight='bold')
    plt.ylabel(ylabel, fontsize=14, fontweight='bold')

    # Создаем кастомную легенду
    legend_elements = [
        mpatches.Patch(color=rehab_colors['0'], label='SCI'),
        mpatches.Patch(color=rehab_colors['1'], label='SCI_TMT'),
        mpatches.Patch(color='#1E88E5', label='Intact')
    ]
    plt.legend(handles=legend_elements, title='Groups', loc='upper right', fontsize=10)

    # Настраиваем оси
    plt.xticks(range(len(days_sorted)), days_sorted, rotation=45)
    plt.grid(True, linestyle='--', alpha=0.7, axis='y')

    plt.tight_layout()
    plt.show()


# Функция для стандартного графика (без выделения)
def create_standard_boxplot(data, x, y, title, ylabel, fig_num):
    plt.figure(fig_num, figsize=(14, 8))

    # Создаем boxplot
    ax = sns.boxplot(data=data, x=x, y=y, hue='Rehab',
                     palette=rehab_colors, showfliers=False, order=available_days)

    # Добавляем заголовок и подписи
    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Day', fontsize=14, fontweight='bold')
    plt.ylabel(ylabel, fontsize=14, fontweight='bold')

    # Настраиваем легенду
    legend = plt.legend(title='Rehab', loc='upper right', fontsize=12)
    legend.get_title().set_fontweight('bold')

    # Настраиваем оси
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.7, axis='y')

    plt.tight_layout()
    plt.show()


# 1. График для Total Count Step (с выделением Day 0)
create_boxplot_with_highlight(df_clean, 'Day_combined', 'Total Count Step',
                              'Total Count Step \n',
                              'Total Count Step', 1)

# 2. График для Average Max Angel (с выделением Day 0)
create_boxplot_with_highlight(df_clean, 'Day_combined', 'Average Max Angel',
                              'Average Maximum Angle \n',
                              'Average Max Angel (degrees)', 2)

# 3. График для Average Min Angel (с выделением Day 0)
create_boxplot_with_highlight(df_clean, 'Day_combined', 'Average Min Angel',
                              'Average Minimum Angle \n',
                              'Average Min Angel (degrees)', 3)

# 4. График для Average Step Duration (с выделением Day 0)
create_boxplot_with_highlight(df_clean, 'Day_combined', 'Average Step Duration (s)',
                              'Average Step Duration \n',
                              'Average Step Duration (seconds)', 4)

# 5. График для Average Height Step (с выделением Day 0)
create_boxplot_with_highlight(df_clean, 'Day_combined', 'Average height Step',
                              'Average Step Height \n',
                              'Average Height Step', 5)

# 6. Дополнительный график: сравнение Max и Min Angel (стандартные цвета)
plt.figure(6, figsize=(16, 8))

# Max Angel
plt.subplot(1, 2, 1)
sns.boxplot(data=df_clean, x='Day_combined', y='Average Max Angel', hue='Rehab',
            palette=rehab_colors, showfliers=False, order=available_days)
plt.title('Average Max Angel', fontsize=14, fontweight='bold')
plt.xlabel('Day', fontsize=12)
plt.ylabel('Angle (degrees)', fontsize=12)
plt.xticks(rotation=45)
legend1 = plt.legend(title='Rehab', loc='upper right')
legend1.get_title().set_fontweight('bold')
plt.grid(True, linestyle='--', alpha=0.7, axis='y')

# Min Angel
plt.subplot(1, 2, 2)
sns.boxplot(data=df_clean, x='Day_combined', y='Average Min Angel', hue='Rehab',
            palette=rehab_colors, showfliers=False, order=available_days)
plt.title('Average Min Angel', fontsize=14, fontweight='bold')
plt.xlabel('Day', fontsize=12)
plt.ylabel('Angle (degrees)', fontsize=12)
plt.xticks(rotation=45)
legend2 = plt.legend(title='Rehab', loc='upper right')
legend2.get_title().set_fontweight('bold')
plt.grid(True, linestyle='--', alpha=0.7, axis='y')

plt.suptitle('Comparison of Maximum and Minimum Angles ',
             fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
plt.show()

# Выводим статистику
print("\n" + "=" * 90)
print("СТАТИСТИКА ПО ГРУППАМ (ДНИ 3 И 7 ОБЪЕДИНЕНЫ)")
print("=" * 90)

for col in columns_to_plot:
    print(f"\n{col}:")
    print("-" * 70)

    # Группируем данные
    grouped = df_clean.groupby(['Day_combined', 'Rehab'])[col].agg(['count', 'mean', 'std', 'min', 'max'])

    for (day, rehab), stats in grouped.iterrows():
        print(f"Day {day}, Rehab={rehab}: n={int(stats['count'])}, "
              f"mean={stats['mean']:.2f}±{stats['std']:.2f}, "
              f"range=[{stats['min']:.2f}, {stats['max']:.2f}]")

# Таблица количества наблюдений
print("\n" + "=" * 90)
print("КОЛИЧЕСТВО НАБЛЮДЕНИЙ ПО ГРУППАМ")
print("=" * 90)
count_table = pd.crosstab(df_clean['Day_combined'], df_clean['Rehab'],
                          margins=True, margins_name='Total')
print(count_table)

# Сохраняем статистику в CSV файл
stats_data = []
for col in columns_to_plot:
    grouped = df_clean.groupby(['Day_combined', 'Rehab'])[col].agg(['count', 'mean', 'std', 'min', 'max']).reset_index()
    grouped['Metric'] = col
    stats_data.append(grouped)

stats_df = pd.concat(stats_data, ignore_index=True)
stats_df = stats_df[['Metric', 'Day_combined', 'Rehab', 'count', 'mean', 'std', 'min', 'max']]
stats_df.to_csv('statistics_by_group.csv', index=False)
print("\nСтатистика сохранена в файл 'statistics_by_group.csv'")