# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton,QComboBox,QListView,QLabel,QTableWidgetItem
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import PointManager

def resizeByRange(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def resizeByScale(x, a, b):
    return  a * (x - b)

class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.plot()

        self.parent = parent

        # キャンバスクリック時のイベント関数を登録
        cid = fig.canvas.mpl_connect('button_press_event', self.onclick)


    def plot(self):
        ax = self.figure.add_subplot(111)

        # map画像の読み込み
        ax.imshow(mpimg.imread('map.png'))

        # 軸を消す
        ax.set_xticks([])
        ax.set_yticks([])

        # 描画
        self.draw()

    def onclick(self, event):
        # print ('(%f, %f) [px]' %(event.xdata, event.ydata))

        # 選択点の描画
        ax = self.figure.axes[0]
        ax.plot(event.xdata, event.ydata, marker='.')
        self.draw()

        origin = [82, 577]      # [px]
        scale = 0.00512295081   # 縮尺[m/px]
        point = [0, 0]
        point[0] = resizeByScale(event.xdata, scale, origin[0])
        point[1] = resizeByScale(-event.ydata, scale, -origin[1])
        self.parent.pm.control_points.append(point)


        self.parent.tableWidget.clearContents()
        items = self.parent.pm.control_points
        print(items)
        self.parent.tableWidget.setRowCount(len(items))

        r = 0
        for item in items:
            self.parent.tableWidget.setItem(r, 1, QTableWidgetItem('{0:.3f}'.format(item[0])))
            self.parent.tableWidget.setItem(r, 2, QTableWidgetItem('{0:.3f}'.format(item[1])))
            r += 1

