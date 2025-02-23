import json
import numpy as np

def get_functions():
    """Запрашивает у пользователя количество и тип функций."""
    num_funcs = int(input("Сколько функций хотите использовать? "))
    functions = []
    for i in range(num_funcs):
        func = input(f"Введите {i+1}-ю функцию (например, sin(x), cos(x), x**2): ")
        functions.append(func)
    return functions

def get_range():
    """Запрашивает у пользователя диапазон x."""
    x_min = float(input("Введите минимальное значение x: "))
    x_max = float(input("Введите максимальное значение x: "))
    num_points = int(input("Сколько точек сгенерировать? "))
    return np.linspace(x_min, x_max, num_points)

def generate_data():
    """Генерирует значения функций в заданном диапазоне."""
    functions = get_functions()
    x_values = get_range()
    data = {"x": x_values.tolist(), "functions": {}}

    for func in functions:
        try:
            y_values = [eval(func, {"x": x, "np": np, "sin": np.sin, "cos": np.cos, "exp": np.exp, "sqrt": np.sqrt}) for x in x_values]
            data["functions"][func] = list(map(float, y_values))  # Приводим к списку float
        except Exception as e:
            print(f"Ошибка в функции '{func}': {e}")

    with open("../data.json", "w") as f:
        json.dump(data, f, indent=4)

    print("Данные успешно сохранены в data.json")

if __name__ == "__main__":
    generate_data()
