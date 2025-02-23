def get_x_range(x_values):
    """Возвращает минимальное и максимальное значение для оси X."""
    return min(x_values), max(x_values)


def get_function_range(functions):
    # Получаем количество точек (длина массива значений одной из функций)
    num_points = len(next(iter(functions.values())))
    # Вычисляем сумму значений функций для каждого x
    sums = [sum(functions[func][i] for func in functions) for i in range(num_points)]
    # Возвращаем минимальное и максимальное значения среди сумм
    return min(sums), max(sums)
