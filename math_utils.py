import math

# Функции для вычислений
def safe_eval_function(func_str):
    allowed_names = {
        'sin': math.sin,
        'cos': math.cos,
        'abs': abs,
        'e': math.e,
        'pi': math.pi,
    }
    try:
        return eval("lambda x: " + func_str.strip(), allowed_names)
    except Exception as e:
        print(f"Ошибка в функции {func_str}: {e}")
        return None
