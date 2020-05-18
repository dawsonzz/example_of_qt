import math
import random
import sys
from PyQt5.QtCore import (QTimer, QPointF, QRectF, Qt)
from PyQt5.QtWidgets import (QApplication, QDialog,
                             QGraphicsItem, QGraphicsScene, QGraphicsView, QHBoxLayout,
                             QPushButton, QSlider, QVBoxLayout)
from PyQt5.QtGui import (QBrush, QColor, QPainter, QPainterPath, QPolygonF)

SCENESIZE = 500


class Head(QGraphicsItem):  # 千足虫头部 图形项
    Rect = QRectF(-30, -20, 60, 40)

    def __init__(self, color, angle, position):
        super(Head, self).__init__()
        self.color = color
        self.angle = angle
        self.setPos(position)

    def boundingRect(self):  # 包围盒矩形
        return Head.Rect

    def shape(self):
        path = QPainterPath()
        path.addEllipse(Head.Rect)  # 椭圆路径，以用于后续碰撞检测
        return path

    def paint(self, painter, option, widget=None):  # 绘制事件
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self.color))
        painter.drawEllipse(Head.Rect)  # 画椭圆头

        # option包含了细节等级（Level of Detail， DOL,是指根据模型的位置和重要度，决定
        # 渲染模型所分配的内存、CPU等计算资源，以降低非重要物体的细节度，提升渲染效率)
        if option.levelOfDetailFromTransform(self.transform()) > 0.5:  # Outer eyes
            # 如果视图没有缩放，则option.levelOfDetailFromTransform(self.transform())返回1.0
            # 如果视图放大为原尺寸的两倍，则返回2.0
            # 如果视图缩小为原尺寸的一半，则返回0.5
            # 根据DOL 决定要不要 绘制 眼镜，眼珠和鼻孔
            painter.setBrush(QBrush(Qt.yellow))
            painter.drawEllipse(-12, -19, 9, 9)  # 画眼，使用图形项自身的逻辑坐标
            painter.drawEllipse(-12, 11, 9, 9)
            if option.levelOfDetailFromTransform(self.transform()) > 0.8:  # Inner eyes
                painter.setBrush(QBrush(Qt.darkBlue))
                painter.drawEllipse(-12, -19, 7, 7)  # 画黑眼珠
                painter.drawEllipse(-12, 11, 7, 7)
                if option.levelOfDetailFromTransform(self.transform()) > 0.9:  # Nostrils
                    painter.setBrush(QBrush(Qt.white))
                    painter.drawEllipse(-27, -5, 2, 2)  # 画鼻孔
                    painter.drawEllipse(-27, 3, 2, 2)

    def advance(self, phase):
        if phase == 0:
            angle = self.angle
            while True:
                flipper = 1
                angle += random.random() * random.choice((-1, 1))  # 角度随机正负摆动
                offset = flipper * random.random()
                x = self.x() + (offset * math.sin(math.radians(angle)))
                y = self.y() + (offset * math.cos(math.radians(angle)))
                if 0 <= x <= SCENESIZE and 0 <= y <= SCENESIZE:
                    break
                else:
                    flipper = -1 if flipper == 1 else 1
            self.angle = angle
            self.position = QPointF(x, y)
        else:
            self.setRotation(random.random() * random.choice((-1, 1)))
            self.setPos(self.position)
            if self.scene():
                for item in self.scene().collidingItems(self):  # 场景的碰撞检测，检测与自身碰撞的项
                    if isinstance(item, Head):  # 如果碰撞的项是头部
                        self.color.setRed(min(255, self.color.red() + 1))  # 则自身（头部）红色分量加一
                    else:  # 如果碰撞的项不是头部
                        item.color.setBlue(min(255, item.color.blue() + 1))  # 则自身（头部）蓝色分量加一


class Segment(QGraphicsItem):
    def __init__(self, color, offset, parent):
        super(Segment, self).__init__(parent)
        self.color = color
        # 每节的身体段
        self.rect = QRectF(offset, -20, 30, 40)
        self.path = QPainterPath()
        self.path.addEllipse(self.rect)

        # 每节的左腿
        x = offset + 15
        y = -20
        self.path.addPolygon(QPolygonF([QPointF(x, y),
                                        QPointF(x - 5, y - 18), QPointF(x - 5, y)]))
        self.path.closeSubpath()
        # 每节的右腿
        y = 20
        self.path.addPolygon(QPolygonF([QPointF(x, y),
                                        QPointF(x - 5, y + 18), QPointF(x - 5, y)]))
        self.path.closeSubpath()
        self.change = 1
        self.angle = 0

    def boundingRect(self):
        return self.path.boundingRect()

    def shape(self):
        return self.path

    def paint(self, painter, option, widget=None):
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self.color))
        if option.levelOfDetailFromTransform(self.transform()) < 0.9:
            painter.drawEllipse(self.rect)
        else:
            painter.drawPath(self.path)

    def advance(self, phase):
        if phase == 0:
            matrix = self.transform()
            matrix.reset()
            self.setTransform(matrix)
            self.angle += self.change * random.random()
            if self.angle > 6:
                self.change = -1
                # self.angle -= 0.00001
            elif self.angle < -6:
                self.change = 1
                # self.angle += 0.00001
        elif phase == 1:
            self.setRotation(self.angle)


class MainForm(QDialog):
    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)
        self.running = False
        self.scene = QGraphicsScene(self)  # 场景
        self.scene.setSceneRect(0, 0, SCENESIZE, SCENESIZE)
        self.scene.setItemIndexMethod(QGraphicsScene.NoIndex)
        self.view = QGraphicsView()  # 创建视图
        self.view.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        self.view.setScene(self.scene)  # 设置视图的场景
        self.view.setFocusPolicy(Qt.NoFocus)
        zoomSlider = QSlider(Qt.Horizontal)  # 水平滑块，用于视图缩放
        zoomSlider.setRange(5, 200)
        zoomSlider.setValue(100)
        self.pauseButton = QPushButton("Pa&use")  # 暂停继续按钮
        quitButton = QPushButton("&Quit")  # 退出按钮
        quitButton.setFocusPolicy(Qt.NoFocus)
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        bottomLayout = QHBoxLayout()
        bottomLayout.addWidget(self.pauseButton)
        bottomLayout.addWidget(zoomSlider)
        bottomLayout.addWidget(quitButton)
        layout.addLayout(bottomLayout)
        self.setLayout(layout)
        self.pauseButton.clicked.connect(self.pauseOrResume)
        zoomSlider.valueChanged[int].connect(self.zoom)
        quitButton.clicked.connect(self.accept)
        self.populate()
        self.startTimer(5)  # 每5ms 产生一次计时器事件
        self.setWindowTitle("Multipedes")

    def zoom(self, value):
        factor = value / 100.0
        matrix = self.view.transform()  # 视图的变换矩阵
        matrix.reset()  # 重置
        matrix.scale(factor, factor)  # 设置x，y缩放比例
        self.view.setTransform(matrix)  # 重新设定视图的变换矩阵

    def pauseOrResume(self):
        self.running = not self.running  # 改变运行状态
        self.pauseButton.setText("Pa&use" if self.running else "Res&ume")  # 改变按钮文本

    def populate(self):  # 生成千足虫
        red, green, blue = 0, 150, 0
        for i in range(random.randint(6, 10)):  # 随机产生6~10条千足虫
            angle = random.randint(0, 360)  # 随机角度
            offset = random.randint(0, SCENESIZE // 2)
            half = SCENESIZE / 2
            x = half + (offset * math.sin(math.radians(angle)))
            y = half + (offset * math.cos(math.radians(angle)))
            color = QColor(red, green, blue)
            head = Head(color, angle, QPointF(x, y))  # 每条虫有1个头

            color = QColor(random.randint(20, 255), random.randint(20, 255), random.randint(20, 255))  # 随机色
            offset = 25
            segment = Segment(color, offset, head)  # 第一节身体段属于头部的子图形项
            for j in range(random.randint(5, 8)):  # 每条虫有6~9个身体节段（1 + (5~8)),randint包含两端
                offset += 25  # 每节 长25
                segment = Segment(color, offset, segment)  # 第n+1节身体段属于第 n节的子图形项
            head.setRotation(random.randint(0, 360))
            self.scene.addItem(head)  # 向场景中添加头部（也会递归地添加个身体段）
        self.running = True

    def timerEvent(self, event):  # 计时器事件的槽
        if not self.running:
            return
        dead = set()  # 死亡集
        items = self.scene.items()  # 场景的所有图形项
        if len(items) == 0:  # 没有虫了就重开
            self.populate()
            return
        heads = set()
        for item in items:
            if isinstance(item, Head):  # 是 头部
                heads.add(item)
                if item.color.red() == 255:  # 头部颜色红色分量达最大时放入死亡集
                    dead.add(item)
        if len(heads) == 1:  # 只剩一只虫时也加入死亡集，以待删除
            dead = heads
        del heads
        # 依次删除死亡集中的头部
        while dead:
            item = dead.pop()  # 从死亡集弹出
            self.scene.removeItem(item)  # 从场景移除头部（会递归地移除子项（各身体段））
            del item
        self.scene.advance()  # 调用各个图形项的 advance()方法


app = QApplication(sys.argv)
form = MainForm()
rect = QApplication.desktop().availableGeometry()
form.resize(int(rect.width() * 0.75), int(rect.height() * 0.9))
form.show()
app.exec_()