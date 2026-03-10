import csv
import random
import numpy as np

# Настройка случайных значений для воспроизводимости
random.seed(42)
np.random.seed(42)

# Параметры групп
GROUP_PARAMS = {
    "Intact": {
        "stride_time_mean": 0.32,
        "stride_time_sd": 0.02,
        "kvar_base": 0.04,
        "asymmetry": 0.0
    },
    "SCI": {
        "stride_time_mean": 0.55,
        "stride_time_sd": 0.10,
        "kvar_base": 0.12,
        "asymmetry": 0.25  # задние лапы хуже
    },
    "SCI_TMT": {
        "stride_time_mean": 0.42,
        "stride_time_sd": 0.06,
        "kvar_base": 0.08,
        "asymmetry": 0.10
    }
}

LIMB_ORDER = [
    "Left front paw",
    "Right front paw",
    "Left hind paw",
    "Left knee",
    "Right hind paw",
    "Right knee"
]

def generate_limb_values(group, limb, base_mean, base_sd, kvar_base, asymmetry):
    # Ухудшение для задних конечностей при SCI
    if "hind" in limb or "knee" in limb:
        mean_adj = base_mean * (1 + asymmetry)
        sd_adj = base_sd * (1 + asymmetry * 1.5)
        kvar_adj = kvar_base * (1 + asymmetry * 2)
    else:
        mean_adj = base_mean
        sd_adj = base_sd
        kvar_adj = kvar_base

    # Генерация
    median = max(0.1, np.random.normal(mean_adj, sd_adj * 0.3))
    mean_val = max(0.1, np.random.normal(mean_adj, sd_adj))
    kvar = max(0.01, np.random.normal(kvar_adj, kvar_adj * 0.3))
    frac = round(1.0 / mean_val, 3) if mean_val > 0 else 0.0

    median_intl = median * random.uniform(0.95, 1.05)
    mean_intl = mean_val * random.uniform(0.95, 1.05)
    kvar_intl = kvar * random.uniform(0.9, 1.1)
    frac_intl = frac * random.uniform(0.95, 1.05)

    return [
        round(median, 3),
        round(mean_val, 3),
        round(kvar, 3),
        round(frac, 3),
        round(median_intl, 3),
        round(mean_intl, 3),
        round(kvar_intl, 3),
        round(frac_intl, 3)
    ]

# Заголовки
header = ["id", "Group", "Day", "Number Rat", "Name video"]
for limb in LIMB_ORDER:
    for param in [
        "Median stride time",
        "Mean stride time",
        "Kvar stride time",
        "Frac stride time",
        "Median stride intl",
        "Mean stride intl",
        "Kvar stride intl",
        "Frac stride intl"
    ]:
        header.append(f"{limb} {param}")

rows = []
id_counter = 1

# Intact: только день 1, 10 крыс
for rat in range(1, 11):
    group = "Intact"
    day = 1
    name_video = f"{group}_day{day}_rat{rat}.mp4"
    params = GROUP_PARAMS[group]
    limb_vals = []
    for limb in LIMB_ORDER:
        limb_vals.extend(generate_limb_values(
            group, limb,
            params["stride_time_mean"],
            params["stride_time_sd"],
            params["kvar_base"],
            params["asymmetry"]
        ))
    rows.append([id_counter, group, day, rat, name_video] + limb_vals)
    id_counter += 1

# SCI и SCI_TMT: дни 3,7,14,21,28; по 10 крыс
for group in ["SCI", "SCI_TMT"]:
    for day in [3, 7, 14, 21, 28]:
        for rat in range(1, 11):
            name_video = f"{group}_day{day}_rat{rat}.mp4"
            params = GROUP_PARAMS[group]
            limb_vals = []
            for limb in LIMB_ORDER:
                limb_vals.extend(generate_limb_values(
                    group, limb,
                    params["stride_time_mean"],
                    params["stride_time_sd"],
                    params["kvar_base"],
                    params["asymmetry"]
                ))
            rows.append([id_counter, group, day, rat, name_video] + limb_vals)
            id_counter += 1

# Сохранение
with open("gait_data_filled.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(rows)

print("Файл 'gait_data_filled.csv' успешно создан!")