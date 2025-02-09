from PySide6.QtGui import QPainter, QPen, QBrush, QFont, QPolygon, Qt
from PySide6.QtCore import QPoint
import math_utils
from left.main import COLORS


def draw_axes(painter, x_min, x_max, y_min, y_max, window_width, window_height, dx, dy):
    # Рисуем оси
    koef_x = window_width / (x_max - x_min if x_max != x_min else 1)
    koef_y = (window_height * 0.8) / (y_max - y_min if y_max != y_min else 1)

    # Вертикальная ось Y
    y_axis_x = dx - x_min * koef_x
    painter.drawLine(y_axis_x, dy, y_axis_x, dy + window_height * 0.8)

    # Горизонтальная ось X
    x_axis_y = dy + window_height * 0.8
    painter.drawLine(dx, x_axis_y, dx + window_width, x_axis_y)

    return koef_x, koef_y


def draw_grid(painter, x_min, x_max, y_min, y_max, koef_x, koef_y, window_width, window_height, dx, dy,
              count_gor_lines):
    # Рисуем сетку и подписи осей
    y_step = (y_max - y_min) / count_gor_lines
    for i in range(count_gor_lines + 1):
        y = y_min + y_step * i
        y_pos = dy + window_height * 0.8 - (y - y_min) * koef_y
        painter.drawLine(dx, y_pos, dx + window_width, y_pos)

        # Подписи для оси Y
        label = f"{y:.2f}" if abs(y) > 1e-2 else "0"
        painter.drawText(dx - 30, y_pos + 10, label)

    x_step = 0.25  # Можешь адаптировать, если нужно
    x = x_min - (x_min % x_step)
    while x <= x_max:
        x_pos = dx + (x - x_min) * koef_x
        painter.drawLine(x_pos, dy, x_pos, dy + window_height * 0.8)

        label = f"{x:.2f}" if abs(x) > 1e-2 else "0"
        painter.drawText(x_pos - 20, dy + window_height * 0.8 + 20, label)
        x += x_step


def draw_graph(painter, points_x, x_min, y_min, koef_x, koef_y, window_height, dx, dy, COLORS):
    for j, points in enumerate(points_x):
        for i in range(len(points)):
            y_pos = dy + window_height * 0.8 - (i - y_min) * koef_y
            x_pos = dx + (points[i] - x_min) * koef_x
            painter.setBrush(QBrush(COLORS[j]))
            painter.setPen(QPen(COLORS[j], 1, Qt.SolidLine))
            painter.drawEllipse(QPoint(x_pos, y_pos), 4, 4)


def draw_legend(painter, functions, dx, window_width):
    font = QFont(painter.font().family(), 15)
    painter.setFont(font)
    y_offset = 10
    for i, func_str in enumerate(functions):
        painter.setBrush(QBrush(COLORS[i]))
        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))
        painter.drawRect(dx + window_width + 70, y_offset + i * 30, 15, 15)
        painter.drawText(dx + window_width + 100, y_offset + i * 30 + 15, f"Функция {i + 1}: {func_str.strip()}")
