from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import math

class Shape(QGraphicsItem):
    line_color = QColor(0, 6, 255)
    point_size = 1.5
    line_size = 1.5
    hsize = 3.0
    def __init__(self, line_color=None, line_size=None, point_size=None, parent=None):
        super(Shape, self).__init__(parent)
        self.points = []
        self.selected = False
        self.painter = QPainter()
        self.hIndex = None
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.closed = False
        self.points_adjusted = None
        self.objtype = None
        self.label = None
        self.editable = False
        self.mode = 0  #0 = 마스킹 , 1 = 수정 , 2 = 화면이동

        if line_color is not None:
            self.line_color = line_color

        if point_size is not None:
            self.point_size = point_size

        if line_size is not None:
            self.line_size = line_size

    def addPoint(self, point):
        self.points.append(point)

    def popPoint(self):
        if self.points:
            return self.points.pop()
        return None

    def paint(self, painter, option, widget):

        if self.points:
            self.prepareGeometryChange()
            color = self.select_line_color if self.selected else self.line_color
            pen = QPen(color)
            pen.setWidth(self.line_size)
            painter.setPen(pen)
            path = self.shape()
            if self.closed == True:
                path.closeSubpath()
            painter.drawPath(path)
            if self.mode == 1:
                vertex_path = QPainterPath()
                self.drawVertex(vertex_path, 0)
                [self.drawVertex(vertex_path, i) for i in range(len(self.points))]
                painter.drawPath(vertex_path)


    def drawVertex(self, path, index):
        path.addEllipse(self.mapFromScene(self.points[index]), 2.5, 2.5)

    def shape(self):
        path = QPainterPath()
        polygon = self.mapFromScene(QPolygonF(self.points))
        path.addPolygon(polygon)
        return path

    def boundingRect(self):
        return self.shape().boundingRect()

    def moveBy(self, tomove, delta):
        if tomove=='all':
            tomove=slice(0,len(self.points))
        else:
            tomove=slice(tomove,tomove+1)
        self.points[tomove] = [point + delta for point in self.points[tomove]]

    def highlightVertex(self, index):
        self.hIndex = index

    def highlightClear(self):
        self.hIndex = None
        self.selected = False

    def select_color(self, color):
        self.line_color = color

    def set_pen_size(self, scale):
        self.line_size /= scale
        self.point_size /= scale

    def set_mode(self, mode):
        self.mode = mode

    def __len__(self):
        return len(self.points)

    def __getitem__(self, index):
        return self.points[index]

    def __setitem__(self, index, value):
        self.points[index] = value


class SubQGraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):
        super(SubQGraphicsScene, self).__init__(parent)
        self.poly = None
        self.line = None
        self.color = QColor(3, 252, 66)
        self.shapeColor = QColor(0, 6, 255)
        self.mode = 0
        self.point_num = 100000000

    def mousePressEvent(self, e):
        pos = e.scenePos()
        if self.mode == 0:
            if e.buttons() == Qt.LeftButton and self.poly == None:
                print("first")
                self.line = Shape(line_color=self.color)
                self.poly = Shape(line_color=self.color)
                self.addItem(self.poly)
                self.addItem(self.line)
                self.line.setPos(pos)
                self.line.points.append(pos)
                self.line.points.append(pos)
                self.line.points[0] = pos
                self.poly.setPos(pos)
                self.poly.addPoint(pos)
                self.poly.setZValue(len(self.poly.points) + 1)
                self.update()

            elif e.buttons() == Qt.LeftButton and self.poly.closed:
                print("closed")
                self.poly.points = []
                self.poly.closed = False
                self.line = Shape(line_color=self.color)
                self.addItem(self.line)
                self.line.setPos(pos)
                self.line.points.append(pos)
                self.line.points.append(pos)
                self.poly.setPos(pos)
                self.poly.addPoint(pos)
                self.poly.setZValue(len(self.poly.points) + 1)
                self.update()

            elif e.buttons() == Qt.LeftButton and self.line == None:
                print("first, last")
                self.line = Shape(line_color=self.color)
                self.addItem(self.poly)
                self.addItem(self.line)
                self.line.setPos(pos)
                self.line.points.append(pos)
                self.line.points.append(pos)
                self.poly.setPos(pos)
                self.poly.addPoint(pos)
                self.poly.setZValue(len(self.poly.points) + 1)
                self.update()

            elif e.buttons() == Qt.LeftButton:
                print("else")
                if len(self.poly.points) == 1:
                    self.addItem(self.poly)
                self.line.points[0] = pos
                self.poly.select_color(self.color)
                self.poly.setPos(pos)
                self.poly.addPoint(pos)
                self.poly.setZValue(len(self.poly.points) + 1)
                self.update()

            elif e.buttons() == Qt.RightButton:
                if self.line != None:
                    self.line.points[1] = self.line.points[0]
                self.poly.closed = True
                self.removeItem(self.line)
                self.update()
                self.line = None

        elif self.mode == 1:
            seed = 100000000
            for i, point in enumerate(self.poly.points):
                dist = math.sqrt(pow(pos.x() - point.x(), 2) + pow(pos.y() - point.y(), 2))
                if seed > dist:
                    seed = dist
                    self.point_num = i
            self.update()


    def mouseMoveEvent(self, e):
        pos = e.scenePos()
        if self.mode == 0:
            if self.line != None:
                self.line.points[1] = pos
                self.update()
        if self.mode == 1 and self.point_num != 100000000:
            self.poly.points[self.point_num] = QPointF(pos.x(), pos.y())
            self.update()

    def mouseReleaseEvent(self,e):
        if self.mode == 1 and self.point_num != 100000000:
            self.point_num = 100000000

    def setPoint(self, points):
        self.poly = Shape(line_color=self.color)
        self.poly.points = points

    def mask_show(self):
        self.poly.closed = True
        self.addItem(self.poly)
        self.update()

    def reset_mask(self):
        self.removeItem(self.poly)
        self.removeItem(self.line)
        self.ploy = None
        self.line = None
        self.update()

    def push_color(self, color):
        self.color = QColor(color[0], color[1], color[2])

    def overrideCursor(self, cursor):
        self._cursor = cursor
        QApplication.setOverrideCursor(cursor)

    def set_poly_mode(self, mode):
        if self.poly != None:
            self.poly.mode = mode

class QViewer(QGraphicsView):

    def __init__(self, parent=None):
        super(QViewer, self).__init__(parent)
        self.scene = SubQGraphicsScene()
        self.photo = QGraphicsPixmapItem()
        self.photo.setZValue(-1)
        self.scene.addItem(self.photo)
        self.setScene(self.scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.NoFrame)
        self.pixmap = QPixmap()

    def setPhoto(self, pixmap=None):
        if pixmap and not pixmap.isNull():
            self.photo.setPixmap(pixmap)
            self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
            self.pixmap = pixmap
        else:
            self.photo.setPixmap(QPixmap())

    def wheelEvent(self, e):
        if not self.photo.pixmap().isNull():
            factor = 1.1
            if e.angleDelta().y() > 0:
                QGraphicsView.scale(self, factor, factor)
            else:
                QGraphicsView.scale(self, 1 / factor, 1 / factor)

    # def mouseMoveEvent(self, e):
    #     mods = int(e.modifiers())
    #     if mods == Qt.ControlModifier:
    #         print("here")
    #         self.fitInView(QRectF(e.x(), e.y(), self.width(), self.height()))


    def reset_scale(self):
        print("미구현")