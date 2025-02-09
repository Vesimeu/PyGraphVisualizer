from PySide6.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton
from PySide6.QtGui import QPainter
from PySide6.QtCore import Qt
import math_utils
import plot_utils

AXES_FONT_SIZE = 11
dx = 60
dy = 100
window_width = 500
window_height = 800
COLORS = [Qt.darkMagenta, Qt.darkBlue, Qt.darkRed]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Графическое отображение")
        self.setMinimumSize(790, 560)
        self.nPoints = 5
        self.pointA = -5
        self.pointB = 5
        self.functions = []  # Список функций
        self.labelNPoints = QLabel("Количество точек", self)
        self.labelNPoints.move(10, 10)
        self.editNPoints = QLineEdit(str(self.nPoints), self)
        self.editNPoints.move(120, 10)
        self.button = QPushButton("Ок", self)
        self.button.move(480, 50)
        self.button.clicked.connect(self.button_clicked)
        self.labelFunction = QLabel("Введите функции через запятую", self)
        self.labelFunction.move(10, 50)
        self.editFunction = QLineEdit(self)
        self.editFunction.move(200, 50)
        self.editFunction.setFixedWidth(200)

    def button_clicked(self):
        # Получаем данные с формы
        self.nPoints = int(self.editNPoints.text())
        self.pointA = float(self.editPointA.text())
        self.pointB = float(self.editPointB.text())

        function_expression = self.editFunction.text()
        if function_expression == "":
            return

        self.functions = function_expression.split(',')
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen()
        pen.setColor("black")
        pen.setWidth(3)
        painter.setPen(pen)
        painter.eraseRect(self.rect())

        if not self.functions:
            return

        points_x = []
        for func_str in self.functions:
            func = math_utils.safe_eval_function(func_str)
            if func:
                points_x.append([func(self.pointA + (self.pointB - self.pointA) * i / (self.nPoints - 1))
                                 for i in range(self.nPoints)])

        # Масштабирование
        x_min = min([min(row) for row in points_x]) if points_x else 0
        x_max = max([max(row) for row in points_x]) if points_x else 0
        y_min = self.pointA
        y_max = self.pointB
        koef_x, koef_y = plot_utils.draw_axes(painter, x_min, x_max, y_min, y_max, window_width, window_height, dx, dy)
        plot_utils.draw_grid(painter, x_min, x_max, y_min, y_max, koef_x, koef_y, window_width, window_height, dx, dy, 8)
        plot_utils.draw_graph(painter, points_x, x_min, y_min, koef_x, koef_y, window_height, dx, dy, COLORS)
        plot_utils.draw_legend(painter, self.functions, dx, window_width)
