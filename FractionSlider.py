#coding:utf-8
import sys
import random
import os
#pyside2's environment conflict with pyqt
envpath = 'D:\Anaconda3\Lib\site-packages\PySide2\plugins\platforms'
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = envpath

from PySide2 import QtCore, QtWidgets, QtGui


class FractionSlider(QtWidgets.QWidget):

    XMARGIN = 12.0
    YMARGIN = 5.0
    WSTRING = "999"

    def __init__(self, numerator=0, denominator=10, parent=None):
        super().__init__()
        self.__numerator = numerator
        self.__denominator = denominator
        self.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                                 QtWidgets.QSizePolicy.Fixed))

    def decimal(self):
        return self.__numerator / float(self.__denominator)

    def fraction(self):
        return self.__numerator, self.__denominator

    def setFraction(self, numerator, denominator=None):
        if denominator is not None:
            if 3 <= denominator <= 60:
                self.__denominator = denominator
            else:
                raise(ValueError, "denominator out of range")

        if 0 <= numerator <= self.__denominator:
            self.__numerator = numerator
        else:
            raise (ValueError, "numerator out of range")

        self.update()
        self.updateGeometry()

    def mousePressEvent(self, event:QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            self.moveSlider(event.x())
            event.accept()
        else:
            QtWidgets.QWidget.mousePressEvent(event)

    def moveSlider(self, x):
        span = self.width() - (FractionSlider.XMARGIN * 2)
        offset = span - x + FractionSlider.XMARGIN
        numerator = int(round(self.__denominator *
                              (1.0 - (offset / span))))
        numerator = max(0, min(numerator, self.__denominator))

        if numerator != self.__numerator:
            self.__numerator = numerator
            self.emit(QtCore.SIGNAL("valueChanged(int, int)"),
                      self.__numerator, self.__denominator)
            self.update()

    def mouseMoveEvent(self, event:QtGui.QMouseEvent):
        self.moveSlider(event.x())

    def sizeHint(self) -> QtCore.QSize:
        return self.minimumSizeHint()

    def minimumSizeHint(self) -> QtCore.QSize:
        font = QtGui.QFont(self.font())
        font.setPointSize(font.pointSize() - 1)
        fm = QtGui.QFontMetricsF(font)
        return QtCore.QSize(fm.width(FractionSlider.WSTRING) * self.__denominator,
                            (fm.height() * 4 + FractionSlider.YMARGIN))

    def paintEvent(self, event:QtGui.QPaintEvent):
        font = QtGui.QFont(self.font())
        font.setPointSize(font.pointSize() - 1)
        fm = QtGui.QFontMetricsF(font)
        fracWidth = fm.width(FractionSlider.WSTRING)
        indent = fm.boundingRect("9").width() / 2.0
        # if not X11:
        #     FracWidth *= 1.5
        span = self.width() - (FractionSlider.XMARGIN * 2)
        value = self.__numerator / float(self.__denominator)

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.TextAntialiasing)
        painter.setPen(self.palette().color(QtGui.QPalette.Mid))
        painter.setBrush(self.palette().brush(QtGui.QPalette.AlternateBase))
        painter.drawRect(self.rect())

        segColor = QtGui.QColor(QtCore.Qt.green).dark(120)
        segLineColor = segColor.dark()
        painter.setPen(segLineColor)
        painter.setBrush(segColor)
        painter.drawRect(FractionSlider.XMARGIN, FractionSlider.YMARGIN,
                         span, fm.height())

        textColor = self.palette().color(QtGui.QPalette.Text)
        segWidth = span/ self.__denominator
        segHeight = fm.height() * 2
        nRect = fm.boundingRect(FractionSlider.WSTRING)
        x = FractionSlider.XMARGIN
        yoffset = segHeight + fm.height()

        for i in range(self.__denominator + 1):
            painter.setPen(segLineColor)
            painter.drawLine(x, FractionSlider.YMARGIN, x, segHeight)
            painter.setPen(textColor)
            y = segHeight
            rect = QtCore.QRectF(nRect)
            rect.moveCenter(QtCore.QPointF(x, y+fm.height() / 2.0))
            painter.drawText(rect, QtGui.Qt.AlignCenter, str(i))
            y = yoffset
            rect.moveCenter(QtCore.QPointF(x, y+fm.height() / 2.0))
            painter.drawText(rect, QtCore.Qt.AlignCenter, str(self.__denominator))
            painter.drawLine(QtCore.QPointF(rect.left() + indent, y),
                             QtCore.QPointF(rect.right() - indent, y))
            x += segWidth

        span = int(span)
        y = FractionSlider.YMARGIN - 0.5
        triangle = [QtCore.QPointF(value * span, y),
                    QtCore.QPointF((value * span) + (2*FractionSlider.XMARGIN), y),
                    QtCore.QPointF((value * span)+ FractionSlider.XMARGIN, fm.height())]
        painter.setPen(QtGui.Qt.yellow)
        painter.setBrush(QtGui.Qt.darkYellow)
        painter.drawPolygon(triangle)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = FractionSlider(100)
    # widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec_())