import sys
import math
import json
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QTabWidget
from PySide6.QtGui import QPainter, QBrush, QColor, QPolygonF, QPen
from PySide6.QtCore import Qt, QPointF
from utils import get_x_range, get_function_range


# Класс для представления отдельного столбца (бара) гистограммы
class Bar:
    def __init__(self, x, y, width, depth, segments):
        """
        x, y - положение основания бара на «земле»
        width, depth - размеры основания
        segments - список кортежей (height, QColor) для накопления
        """
        self.x = x
        self.y = y
        self.width = width
        self.depth = depth
        self.segments = segments


# Виджет для отрисовки одного графика с возможностью интерактивного вращения и перемещения
class GraphWidget(QWidget):
    def __init__(self, bars, x_min=None, x_max=None, z_min=None, z_max=None, x_values=None, legend_items=None,
                 draw_axes_after=False, parent=None):
        super().__init__(parent)
        self.bars = bars
        self.x_values = x_values
        self.azimuth = 45
        self.elevation = 30
        self.last_mouse_pos = None
        self.scale_factor = 1.0  # Коэффициент масштабирования
        self.draw_axes_after = draw_axes_after
        self.x_min = x_min
        self.x_max = x_max
        self.z_min = z_min
        self.z_max = z_max
        self.legend_items = legend_items if legend_items is not None else []  # Элементы легенды
        self.x_offset = 0  # Смещение по X для перемещения камеры
        self.y_offset = 0  # Смещение по Y для перемещения камеры

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # Центрирование рисунка в окне
        center_offset = QPointF(self.width() / 2, self.height() / 2)

        # Рисуем оси на заднем плане, если нужно
        if not self.draw_axes_after:
            self.draw_axes(painter, center_offset, self.x_min, self.x_max, self.z_min, self.z_max, self.x_values)

        # Отрисовка баров
        for bar in self.bars:
            base_z = 0
            for (h, color) in bar.segments:
                self.draw_cuboid(painter, bar.x, bar.y, base_z, bar.width, bar.depth, h, center_offset, color)
                base_z += h

        # Рисуем оси поверх баров, если нужно
        if self.draw_axes_after:
            self.draw_axes(painter, center_offset, self.x_min, self.x_max, self.z_min, self.z_max, self.x_values)

        # Рисуем легенду
        if self.legend_items:
            self.draw_legend(painter)

        painter.end()

    def draw_legend(self, painter):
        """Рисует легенду в правом верхнем углу."""
        legend_x = self.width() - 150  # Отступ от правого края
        legend_y = 10  # Отступ сверху
        box_size = 20  # Размер цветного квадрата
        spacing = 5  # Расстояние между элементами
        for i, (name, color) in enumerate(self.legend_items):
            # Цветной квадрат
            painter.setBrush(QBrush(color))
            painter.drawRect(legend_x, legend_y + i * (box_size + spacing), box_size, box_size)
            # Текст
            painter.setPen(QPen(Qt.black))
            painter.drawText(legend_x + box_size + 5, legend_y + i * (box_size + spacing) + box_size / 2 + 5, name)

    def wheelEvent(self, event):
        """Обрабатывает прокрутку колесика мыши для масштабирования графика."""
        delta = event.angleDelta().y()
        scale_step = 0.1
        if delta > 0:
            self.scale_factor *= (1 + scale_step)
        else:
            self.scale_factor /= (1 + scale_step)
        self.update()

    def project_point(self, x, y, z, offset):
        """Проецирует 3D точку на 2D экран с учётом вращения, масштабирования и смещения."""
        rad_az = math.radians(self.azimuth)
        X1 = x * math.cos(rad_az) - y * math.sin(rad_az)
        Y1 = x * math.sin(rad_az) + y * math.cos(rad_az)
        Z1 = z
        rad_el = math.radians(self.elevation)
        Y2 = Y1 * math.cos(rad_el) - Z1 * math.sin(rad_el)
        Z2 = Y1 * math.sin(rad_el) + Z1 * math.cos(rad_el)
        # Добавляем смещение камеры
        screen_x = X1 * self.scale_factor + offset.x() + self.x_offset
        screen_y = Y2 * self.scale_factor + offset.y() + self.y_offset
        return QPointF(screen_x, screen_y)

    def draw_cuboid(self, painter, x, y, z, w, d, h, offset, color):
        vertices = {}
        vertices['A'] = self.project_point(x, y, z, offset)
        vertices['B'] = self.project_point(x + w, y, z, offset)
        vertices['C'] = self.project_point(x + w, y + d, z, offset)
        vertices['D'] = self.project_point(x, y + d, z, offset)
        vertices['E'] = self.project_point(x, y, z + h, offset)
        vertices['F'] = self.project_point(x + w, y, z + h, offset)
        vertices['G'] = self.project_point(x + w, y + d, z + h, offset)
        vertices['H'] = self.project_point(x, y + d, z + h, offset)

        top_face = [vertices[k] for k in ['E', 'F', 'G', 'H']]
        painter.setBrush(QBrush(color.lighter(120)))
        painter.drawPolygon(QPolygonF(top_face))

        right_face = [vertices[k] for k in ['B', 'C', 'G', 'F']]
        painter.setBrush(QBrush(color.darker(120)))
        painter.drawPolygon(QPolygonF(right_face))

        left_face = [vertices[k] for k in ['A', 'D', 'H', 'E']]
        painter.setBrush(QBrush(color))
        painter.drawPolygon(QPolygonF(left_face))

        front_face = [vertices[k] for k in ['A', 'B', 'F', 'E']]
        painter.setBrush(QBrush(color.darker(150)))
        painter.drawPolygon(QPolygonF(front_face))

    def draw_axes(self, painter, offset, x_min, x_max, z_min, z_max, x_values, x_tick_step=2):
        if not self.bars:
            return

        # Цвет осей - тёмно-серый, толщина 5px
        axis_pen = QPen(QColor(50, 50, 50), 5)
        painter.setPen(axis_pen)

        # Определяем начальную точку (левый нижний угол)
        origin = self.project_point(x_min, 0, 0, offset)

        # Ось X
        x_end = self.project_point(x_max, 0, 0, offset)
        painter.drawLine(origin, x_end)
        self.draw_arrow(painter, origin, x_end)

        # Ось Z
        z_end = self.project_point(x_min, 0, z_max, offset)
        painter.drawLine(origin, z_end)
        self.draw_arrow(painter, origin, z_end)



        # Вспомогательная сетка с контрастным цветом и сплошными линиями
        grid_pen = QPen(QColor(255, 255, 255), 1, Qt.SolidLine)  # Белый цвет, сплошная линия
        painter.setPen(grid_pen)

        # Вертикальные линии сетки (по X)
        for i in range(0, len(x_values), x_tick_step):
            x_pos = self.bars[i].x + self.bars[i].width / 2
            grid_start = self.project_point(x_pos, 0, z_min, offset)
            grid_end = self.project_point(x_pos, 0, z_max, offset)
            painter.drawLine(grid_start, grid_end)

        # Горизонтальные линии сетки (по Z) с большим количеством линий
        num_z_ticks = 10  # Увеличиваем количество линий
        tick_interval_z = (z_max - z_min) / num_z_ticks
        current_z = z_min
        while current_z <= z_max:
            grid_start = self.project_point(x_min, 0, current_z, offset)
            grid_end = self.project_point(x_max + x_pos, 0, current_z, offset)
            painter.drawLine(grid_start, grid_end)
            current_z += tick_interval_z

        # Подписи оси X
        painter.setPen(QPen(Qt.black, 2))
        for i in range(0, len(x_values), x_tick_step):
            x_pos = self.bars[i].x + self.bars[i].width / 2
            tick_pt = self.project_point(x_pos, 0, 0, offset)
            painter.drawText(tick_pt + QPointF(-10, 75), f"{x_values[i]:.1f}")

        # Подписи оси Z
        current_z = z_min
        while current_z <= z_max:
            tick_pt = self.project_point(x_min, 0, current_z, offset)
            painter.drawText(tick_pt + QPointF(-35, 0), f"{current_z / 50:.2f}")
            current_z += tick_interval_z

    def draw_arrow(self, painter, start, end):
        line_vec = QPointF(end.x() - start.x(), end.y() - start.y())
        length = math.hypot(line_vec.x(), line_vec.y())
        if length == 0:
            return
        norm = QPointF(line_vec.x() / length, line_vec.y() / length)
        arrow_size = 10
        angle = math.radians(30)
        wing1 = QPointF(
            end.x() - arrow_size * (norm.x() * math.cos(angle) + norm.y() * math.sin(angle)),
            end.y() - arrow_size * (-norm.x() * math.sin(angle) + norm.y() * math.cos(angle))
        )
        wing2 = QPointF(
            end.x() - arrow_size * (norm.x() * math.cos(angle) - norm.y() * math.sin(angle)),
            end.y() - arrow_size * (norm.x() * math.sin(angle) + norm.y() * math.cos(angle))
        )
        painter.drawLine(end, wing1)
        painter.drawLine(end, wing2)

    def mousePressEvent(self, event):
        self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.last_mouse_pos is not None:
            dx = event.x() - self.last_mouse_pos.x()
            dy = event.y() - self.last_mouse_pos.y()
            if event.modifiers() & Qt.ShiftModifier:
                # Перемещаем камеру при зажатом Shift
                self.x_offset += dx
                self.y_offset += dy
            else:
                # Вращаем график без Shift
                self.azimuth += dx * 0.5
                self.elevation += dy * 0.5
            self.last_mouse_pos = event.pos()
            self.update()


# Функция для генерации баров с накоплением
def load_data(filename):
    with open(filename, 'r') as file:
        return json.load(file)


def generate_bars_from_data(data, bar_width=10, bar_depth=10, scale=50, bar_spacing=5):
    bars = []
    x_values = data["x"]
    functions = data["functions"]

    colors = [QColor(200, 0, 0), QColor(0, 0, 200), QColor(0, 200, 0)]
    function_names = list(functions.keys())

    for i, x in enumerate(x_values):
        y = 0
        segments = []
        base_z = 0

        for j, func_name in enumerate(function_names):
            value = functions[func_name][i] * scale
            segments.append((value, colors[j % len(colors)]))
            base_z += value

        x_position = i * (bar_width + bar_spacing)
        bars.append(Bar(x_position, y, bar_width, bar_depth, segments))

    return bars


# Главное окно с вкладками
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Гистограмма с накоплением и вращением")
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        self.initUI(data)

    def initUI(self, data):
        x_min, x_max = get_x_range(data["x"])
        z_min, z_max = get_function_range(data["functions"])
        z_min *= 50
        z_max *= 50

        # Создаём элементы легенды
        colors = [QColor(200, 0, 0), QColor(0, 0, 200), QColor(0, 200, 0)]
        function_names = list(data["functions"].keys())
        legend_items = list(zip(function_names, colors[:len(function_names)]))

        bars_stacked = generate_bars_from_data(data, bar_spacing=2)
        graph_stacked = GraphWidget(bars_stacked, x_min, x_max, z_min, z_max, data["x"], legend_items,
                                    draw_axes_after=False)

        self.tab_widget.addTab(graph_stacked, "Stacked Demo")


if __name__ == '__main__':
    data = load_data("../data.json")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())