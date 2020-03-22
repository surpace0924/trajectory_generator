# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton,QComboBox,QListView,QLabel,QTableWidgetItem
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import PointManager
import CatmullRom

def resizeByRange(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def resizeByScale(x, a, b):
    return  a * (x - b)

def convertToMeter(px, scale, origin):
    result = [0, 0]
    result[0] = scale * (px[0] - origin[0])
    result[1] = scale * (-px[1] + origin[1])
    return result

def convertToPx(meter, scale, origin):
    result = [0, 0]
    result[0] = origin[0] + (meter[0] / scale)
    result[1] = origin[1] - (meter[1] / scale)
    return result

class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.plot()

        self.parent = parent
        self.origin = [82, 577]      # [px]
        self.scale = 0.00512295081   # 縮尺[m/px]

        # キャンバスクリック時のイベント関数を登録
        cid = fig.canvas.mpl_connect('button_press_event', self.onclick)

    def plot(self):
        # map画像の読み込み
        self.ax.imshow(mpimg.imread('map.png'))

        # 軸を消す
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        # 描画
        self.draw()

    def onclick(self, event):
        # print ('(%f, %f) [px]' %(event.xdata, event.ydata))

        # 選択点の描画
        self.ax.plot(event.xdata, event.ydata, marker='.', color="green")
        self.draw()

        clicked_px =  [event.xdata, event.ydata]
        point = convertToMeter(clicked_px, self.scale, self.origin)
        self.parent.pm.control_points.append(point)

        self.parent.tableWidget.clearContents()
        items = self.parent.pm.control_points
        self.parent.tableWidget.setRowCount(len(items))

        r = 0
        for item in items:
            self.parent.tableWidget.setItem(r, 1, QTableWidgetItem('{0:.3f}'.format(item[0])))
            self.parent.tableWidget.setItem(r, 2, QTableWidgetItem('{0:.3f}'.format(item[1])))
            r += 1

    def drawTrajectory(self):
        ax = self.figure.axes[0]
        points = np.array(self.parent.pm.control_points)
        cr = CatmullRom.CatmullRom()
        dots = []
        cr.setControlPoint(points)
        cr.calculate()
        dots = cr.getResult()

        dots = np.array(dots)
        dot_px = []
        for i in range(len(dots)):
            dot_px.append(convertToPx(dots[i], self.scale, self.origin))
            self.ax.plot(dot_px[i][0], dot_px[i][1], marker='.', color="red")

        self.draw()
