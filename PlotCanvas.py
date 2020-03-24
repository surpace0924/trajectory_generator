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
        self.control_point = None
        self.traj = None

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
        # self.ax.plot(event.xdata, event.ydata, marker='.', color="green")
        # self.draw()

        # pxからmへ単位を変換し，制御点を管理するクラスへ書き込み
        clicked_px =  [event.xdata, event.ydata]
        point = convertToMeter(clicked_px, self.scale, self.origin)
        self.parent.pm.control_points.append(point)

        # tableをクリアし，座標の数だけ行を用意
        items = self.parent.pm.control_points
        self.parent.tableWidget.clearContents()
        self.parent.tableWidget.setRowCount(len(items))

        # tableへの書き込み
        r = 0
        for item in items:
            self.parent.tableWidget.setItem(r, 0, QTableWidgetItem('{0:.3f}'.format(item[0])))
            self.parent.tableWidget.setItem(r, 1, QTableWidgetItem('{0:.3f}'.format(item[1])))
            r += 1

        # self.drawControlPoint(self.parent.pm.control_points)

    def drawControlPoint(self, point):
        # すでに点が描かれている場合はそれを消す
        if self.control_point != None:
            self.control_point[0].remove()
            print(self.control_point)

        dot_px = []
        for i in range(len(point)):
            dot_px.append(convertToPx(point[i], self.scale, self.origin))
        plot_x , plot_y = self.__convertToPlot(dot_px)
        self.control_point = self.ax.plot(plot_x, plot_y, marker='.', color="green", linestyle='None')
        self.draw()

    def drawTrajectory(self):
        ax = self.figure.axes[0]
        points = np.array(self.parent.pm.control_points)
        cr = CatmullRom.CatmullRom()
        dots = []
        cr.setControlPoint(points)
        cr.calculate()
        dots, length = cr.getResult()

        dots = np.array(dots)
        dot_px = []

        # すでに経路が描かれている場合はそれを消す
        if self.traj != None:
            self.traj[0].remove()

        for i in range(len(dots)):
            dot_px.append(convertToPx(dots[i], self.scale, self.origin))

        # 描画用に座標リストを2つのベクトルに変換
        plot_x , plot_y = self.__convertToPlot(dot_px)

        # 描画
        self.traj = self.ax.plot(plot_x, plot_y, marker='.', color="red")
        self.draw()

    # Matplotlibに入れるために座標リストを2つのベクトルに変換する
    # [[x1, y1], [x2, y2], ...] -> [x1, x2, ...], [y1, y2, ...]
    def __convertToPlot(self, matrix):
        x = []
        y = []
        for i in range(len(matrix)):
            x.append(matrix[i][0])
            y.append(matrix[i][1])
        return x, y
