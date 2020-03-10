# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton,QComboBox,QListView,QLabel
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import PlotCanvas


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

        # キャンバスクリック時のイベント関数を登録
        cid = fig.canvas.mpl_connect('button_press_event', self.onclick)

        print(self)


    def plot(self):
        ax = self.figure.add_subplot(111)

        # map画像の読み込み
        ax.imshow(mpimg.imread('map.png'))

        # 軸を消す
        ax.set_xticks([])
        ax.set_yticks([])

        # 描画
        self.draw()

        print(self)

    def onclick(self, event):
        # print ('(%f, %f) [px]' %(event.xdata, event.ydata))
        origin = [82, 577]      # [px]
        scale = 0.00512295081   # 縮尺[m/px]
        point = [0, 0]
        point[0] = resizeByScale(event.xdata, scale, origin[0])
        point[1] = resizeByScale(-event.ydata, scale, -origin[1])

        ax = self.figure.axes[0]
        ax.plot(event.xdata, event.ydata, marker='.')
        self.draw()

