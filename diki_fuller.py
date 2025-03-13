from statsmodels.tsa.stattools import adfuller


def func_diki_fuller(X_raw, dt):
    count_stat = 0
    count_not_stat = 0
    for i in range(0, len(X_raw) - dt, dt):
        result = adfuller(X_raw[i:i + dt])

        # Вывести результаты
        print('ADF Statistic: %f' % result[0])
        print('p-value: %f' % result[1])
        print('Critical Values:')
        for key, value in result[4].items():
            print('\t%s: %.3f' % (key, value))

        # Интерпретация

        alpha = 0.05  # Уровень значимости
        print("\nИнтерпретация:")
        if result[1] <= alpha:
            print("p-value меньше или равно уровню значимости.  Отвергаем нулевую гипотезу.")
            print("Временной ряд стационарен.")
            count_stat += 1
        else:
            print("p-value больше уровня значимости.  Не отвергаем нулевую гипотезу.")
            print("Нет оснований утверждать, что временной ряд стационарен.")
            count_not_stat += 1
    print(f'количество стационарных участков {count_stat}')
    print(f'количество стационарных участков {count_not_stat}')
