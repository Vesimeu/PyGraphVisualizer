import json


def get_x_range(x_values):
    """Возвращает минимальное и максимальное значение для оси X."""
    return min(x_values), max(x_values)


def get_function_range(functions):
    # Получаем количество точек (длина массива значений одной из функций)
    num_points = len(next(iter(functions.values())))
    # Вычисляем сумму значений функций для каждого x
    sums = [sum(functions[func][i] for func in functions) for i in range(num_points)]
    # Возвращаем минимальное и максимальное значения среди сумм
    #TODO: добавить ноль
    return min(sums), max(sums)


def calculate_koef(data, base_target_height=3):
    """
    Вычисляет коэффициент koef на основе данных функций с учётом нормализации.

    :param data: словарь с данными (x и functions)
    :param base_target_height: базовая целевая высота для масштабирования (по умолчанию 3)
    :return: коэффициент koef
    """
    # Получаем все значения функций
    functions = data["functions"]
    all_values = []
    for func_name in functions:
        all_values.extend(functions[func_name])

    # Находим максимальное абсолютное значение
    max_value = max(abs(min(all_values)), abs(max(all_values)))

    if max_value == 0:  # Избегаем деления на ноль
        return 1.0

    # Если максимальное значение большое (>10), нормализуем его к базовому диапазону
    if max_value > 10:
        # Приводим максимальное значение к диапазону около 1 и умножаем на базовую высоту
        normalization_factor = 1 / (max_value / 10)  # Примерно масштабируем к 10
        koef = base_target_height * normalization_factor
    else:
        # Для небольших значений (около 1) используем base_target_height напрямую
        koef = base_target_height

    return koef

# Функция для генерации баров с накоплением
def load_data(filename):
    with open(filename, 'r') as file:
        return json.load(file)

