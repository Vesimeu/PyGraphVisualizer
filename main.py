import sys
import math
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QTabWidget
from PySide6.QtGui import QPainter, QBrush, QColor, QPolygonF, QPen
from PySide6.QtCore import Qt, QPointF


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


# Виджет для отрисовки одного графика с возможностью интерактивного вращения
class GraphWidget(QWidget):
    def __init__(self, bars, draw_axes_after=False, parent=None):
        super().__init__(parent)
        self.bars = bars
        # Параметры для вращения (азимут и угол наклона)
        self.azimuth = 45  # поворот вокруг вертикальной оси (ось Z)
        self.elevation = 30  # угол наклона (относительно горизонта)
        self.last_mouse_pos = None
        # Флаг: оси рисовать после баров (на переднем плане) или перед (на заднем плане)
        self.draw_axes_after = draw_axes_after

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # Центрирование рисунка в окне
        center_offset = QPointF(self.width() / 2, self.height() / 2)

        # Если оси нужно рисовать на заднем плане, то сначала рисуем оси
        if not self.draw_axes_after:
            self.draw_axes(painter, center_offset)

        # Отрисовка баров (накопление реализовано путем последовательного сложения сегментов)
        for bar in self.bars:
            base_z = 0  # начальная высота для накопления сегментов
            for (h, color) in bar.segments:
                self.draw_cuboid(painter, bar.x, bar.y, base_z, bar.width, bar.depth, h, center_offset, color)
                base_z += h  # следующий сегмент располагается выше предыдущего

        # Если оси нужно рисовать поверх, то делаем это после баров
        if self.draw_axes_after:
            self.draw_axes(painter, center_offset)
        painter.end()

    def project_point(self, x, y, z, offset):
        """
        Проецирует 3D точку (x, y, z) на 2D экран с учетом вращения.
        Сначала выполняется поворот вокруг оси Z (азимут), затем наклон (elevation) вокруг оси X.
        """
        # Вращение вокруг оси Z: поворот в плоскости XY
        rad_az = math.radians(self.azimuth)
        X1 = x * math.cos(rad_az) - y * math.sin(rad_az)
        Y1 = x * math.sin(rad_az) + y * math.cos(rad_az)
        Z1 = z
        # Наклон вокруг оси X: поворот в плоскости YZ
        rad_el = math.radians(self.elevation)
        Y2 = Y1 * math.cos(rad_el) - Z1 * math.sin(rad_el)
        Z2 = Y1 * math.sin(rad_el) + Z1 * math.cos(rad_el)
        # Для ортографической проекции используем X1 и Y2
        return QPointF(X1 + offset.x(), Y2 + offset.y())

    def draw_cuboid(self, painter, x, y, z, w, d, h, offset, color):
        # Вычисляем 8 вершин параллелепипеда
        vertices = {}
        vertices['A'] = self.project_point(x, y, z, offset)
        vertices['B'] = self.project_point(x + w, y, z, offset)
        vertices['C'] = self.project_point(x + w, y + d, z, offset)
        vertices['D'] = self.project_point(x, y + d, z, offset)
        vertices['E'] = self.project_point(x, y, z + h, offset)
        vertices['F'] = self.project_point(x + w, y, z + h, offset)
        vertices['G'] = self.project_point(x + w, y + d, z + h, offset)
        vertices['H'] = self.project_point(x, y + d, z + h, offset)

        # Рисуем три видимые грани: верхнюю, правую и левую
        # Верхняя грань
        top_face = [vertices[k] for k in ['E', 'F', 'G', 'H']]
        painter.setBrush(QBrush(color.lighter(120)))
        painter.drawPolygon(QPolygonF(top_face))

        # Правая грань
        right_face = [vertices[k] for k in ['B', 'C', 'G', 'F']]
        painter.setBrush(QBrush(color.darker(120)))
        painter.drawPolygon(QPolygonF(right_face))

        # Левая грань
        left_face = [vertices[k] for k in ['A', 'D', 'H', 'E']]
        painter.setBrush(QBrush(color))
        painter.drawPolygon(QPolygonF(left_face))

        # Дополнительная фронтальная грань (вдоль высоты)
        front_face = [vertices[k] for k in ['A', 'B', 'F', 'E']]
        painter.setBrush(QBrush(color.darker(150)))
        painter.drawPolygon(QPolygonF(front_face))

    def draw_axes(self, painter, offset):
        """
        Отрисовка осей:
         - X: горизонтальная (категорий),
         - Y: ось глубины,
         - Z: вертикальная (значений).
        Оси снабжены стрелками и отметками.
        """
        if not self.bars:
            return

        # Определяем границы по барам
        min_x = min(bar.x for bar in self.bars)
        max_x = max(bar.x + bar.width for bar in self.bars)
        min_y = min(bar.y for bar in self.bars)
        max_y = max(bar.y + bar.depth for bar in self.bars)
        max_z = max(sum(h for h, _ in bar.segments) for bar in self.bars)

        pen = QPen(Qt.black, 2)
        painter.setPen(pen)

        # Начало координат – точка (min_x, min_y, 0)
        origin = self.project_point(min_x, min_y, 0, offset)
        # Ось X: от (min_x, min_y, 0) до (max_x, min_y, 0)
        x_end = self.project_point(max_x, min_y, 0, offset)
        painter.drawLine(origin, x_end)
        self.draw_arrow(painter, origin, x_end)

        # Ось Y: от (min_x, min_y, 0) до (min_x, max_y, 0)
        y_end = self.project_point(min_x, max_y, 0, offset)
        painter.drawLine(origin, y_end)
        self.draw_arrow(painter, origin, y_end)

        # Ось Z: от (min_x, min_y, 0) до (min_x, min_y, max_z)
        z_end = self.project_point(min_x, min_y, max_z, offset)
        painter.drawLine(origin, z_end)
        self.draw_arrow(painter, origin, z_end)

        # Отметки по оси X
        tick_interval_x = 50
        tick_length = 5
        current_x = min_x
        while current_x <= max_x:
            tick_pt = self.project_point(current_x, min_y, 0, offset)
            dx = x_end.x() - origin.x()
            dy = x_end.y() - origin.y()
            length = math.hypot(dx, dy)
            perp = QPointF(-dy / length, dx / length) if length != 0 else QPointF(0, 0)
            tick_start = QPointF(tick_pt.x() + perp.x() * tick_length, tick_pt.y() + perp.y() * tick_length)
            tick_end = QPointF(tick_pt.x() - perp.x() * tick_length, tick_pt.y() - perp.y() * tick_length)
            painter.drawLine(tick_start, tick_end)
            painter.drawText(tick_pt + QPointF(5, 5), f"{current_x:.0f}")
            current_x += tick_interval_x

        # Отметки по оси Z
        tick_interval_z = 50
        current_z = 0
        while current_z <= max_z:
            tick_pt = self.project_point(min_x, min_y, current_z, offset)
            dx = z_end.x() - origin.x()
            dy = z_end.y() - origin.y()
            length = math.hypot(dx, dy)
            perp = QPointF(-dy / length, dx / length) if length != 0 else QPointF(0, 0)
            tick_start = QPointF(tick_pt.x() + perp.x() * tick_length, tick_pt.y() + perp.y() * tick_length)
            tick_end = QPointF(tick_pt.x() - perp.x() * tick_length, tick_pt.y() - perp.y() * tick_length)
            painter.drawLine(tick_start, tick_end)
            painter.drawText(tick_pt + QPointF(5, 5), f"{current_z:.0f}")
            current_z += tick_interval_z

    def draw_arrow(self, painter, start, end):
        """
        Рисует стрелку на конце линии.
        """
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
            # Изменяем азимут и угол наклона пропорционально смещению мыши
            self.azimuth += dx * 0.5
            self.elevation += dy * 0.5
            self.last_mouse_pos = event.pos()
            self.update()


# Функция для генерации баров с накоплением (две сегмента в каждом баре)
def generate_bars_stacked(num_bars=20, bar_width=20, bar_depth=20, scale=50):
    bars = []
    gap = 10
    for i in range(num_bars):
        x = i * (bar_width + gap)
        y = 0
        angle = i * (2 * math.pi / (num_bars - 1))
        # Демонстрация накопления: два сегмента (70% и 30% от общего значения)
        total = (math.sin(angle) + 1) * scale  # значение от 0 до 2*scale
        lower = total * 0.7
        upper = total * 0.3
        bars.append(Bar(x, y, bar_width, bar_depth, [(lower, QColor(200, 0, 0)), (upper, QColor(0, 0, 200))]))
    return bars


# Главное окно с вкладками
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Гистограмма с накоплением и вращением")
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        self.initUI()

    def initUI(self):
        # График с демонстрацией накопления
        bars_stacked = generate_bars_stacked(num_bars=20, bar_width=20, bar_depth=20, scale=50)
        graph_stacked = GraphWidget(bars_stacked, draw_axes_after=False)
        self.tab_widget.addTab(graph_stacked, "Stacked Demo")
        # Можно добавить дополнительные вкладки с другими данными


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
