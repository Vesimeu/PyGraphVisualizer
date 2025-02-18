def get_x_range(x_values):
    """Возвращает минимальное и максимальное значение для оси X."""
    return min(x_values), max(x_values)


def get_function_range(functions):
    """Возвращает минимальное и максимальное значение для оси Z (значений функций)."""
    min_val = float('inf')
    max_val = float('-inf')

    for func_values in functions.values():
        min_val = min(min_val, min(func_values))
        max_val = max(max_val, max(func_values))

    return min_val, max_val
