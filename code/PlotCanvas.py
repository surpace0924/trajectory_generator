# -*- coding: utf-8 -*-

import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton, QComboBox, QListView, QLabel, QTableWidgetItem
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches
import numpy as np
import colorsys


def resizeByRange(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def resizeByScale(x, a, b):
    return a * (x - b)

# [px]から[m]へ単位を変換
def convertToMeter(px, scale, origin):
    result = [0, 0]
    result[0] = scale * (px[0] - origin[0])
    result[1] = scale * (-px[1] + origin[1])
    return result

# [m]から[px]へ単位を変換
def convertToPx(meter, scale, origin):
    result = [0, 0]
    result[0] = origin[0] + (meter[0] / scale)
    result[1] = origin[1] - (meter[1] / scale)
    return result


class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        # 各種パラメータ
        self.parent = parent
        self.origin = [380, 380]                                       # 原点の座標[px]
        self.scale = 0.01593                                      # 縮尺[m/px]
        self.map_path = os.path.dirname(__file__) + "/../map/2021.png" # map画像のパス
        self.control_point = None
        self.traj = None
        self.origin_point = None

        # 描画エリアの初期設定
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = fig.add_subplot(111)
        self.ax.set_position([0, 0, 1, 1])
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.add_zoom_func()
        self.plot()

        # キャンバスクリック時のイベント関数を登録
        cid = fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.drawOrigin(self.origin)

    def plot(self):
        # map画像の読み込み
        self.img = mpimg.imread(self.map_path)
        self.ax.imshow(self.img)

        # 軸を消す
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        # 描画
        self.draw()

    # 原点の描画
    def drawOrigin(self, point):
        self.origin = point
        # すでに点が描かれている場合はそれを消す
        if self.origin_point != None:
            self.origin_point[0].remove()

        dot_px = []
        plot_x, plot_y = self.__convertToPlot(dot_px)
        self.origin_point = self.ax.plot(self.origin[0], self.origin[1], marker='.', markersize=12, color="yellow", linestyle='None')
        self.draw()

    # mapクリック時の処理
    def onclick(self, event):
        # pxからmへ単位を変換し，制御点を管理するクラスへ書き込み
        clicked_px = [event.xdata, event.ydata]
        point = convertToMeter(clicked_px, self.scale, self.origin)
        point.append(0)# 角度はとりあえず0としておく
        self.parent.via_point.append(point)

        # tableをクリアし，座標の数だけ行を用意
        items = self.parent.via_point
        # self.parent.tableWidget.clearContents()
        self.parent.tableWidget.setRowCount(len(items))

        # tableへの書き込み
        r = len(items)-1
        self.parent.tableWidget.setItem(
            r, 0, QTableWidgetItem('{0:.3f}'.format(items[r][0])))
        self.parent.tableWidget.setItem(
            r, 1, QTableWidgetItem('{0:.3f}'.format(items[r][1])))
        self.parent.tableWidget.setItem(
            r, 2, QTableWidgetItem('{0:.3f}'.format(items[r][2])))
        # print()


    def drawControlPoint(self, point):
        # すでに点が描かれている場合はそれを消す
        if self.control_point != None:
            self.control_point[0].remove()

        dot_px = []
        for i in range(len(point)):
            dot_px.append(convertToPx(point[i], self.scale, self.origin))

        plot_x, plot_y = self.__convertToPlot(dot_px)
        self.control_point = self.ax.plot(
            plot_x, plot_y, marker='.', markersize=12, color="green", linestyle='None')
        self.draw()

    def drawTrajectory(self, dots, speed_profile):
        ax = self.figure.axes[0]
        dots = np.array(dots)
        dot_px = []

        # すでに経路が描かれている場合はそれを消す
        if self.traj != None:
            self.traj.remove()

        for i in range(len(dots)):
            dot_px.append(convertToPx(dots[i], self.scale, self.origin))

        # 描画用に座標リストを2つのベクトルに変換
        plot_x, plot_y = self.__convertToPlot(dot_px)

        color_list = []
        max_speed = max(speed_profile)
        for speed in speed_profile:
            rgb = colorsys.hsv_to_rgb(0.7*(1-(speed / max_speed)), 1, 1)
            color_list.append([rgb[0], rgb[1], rgb[2]])

        # 描画
        self.traj = self.ax.scatter(plot_x, plot_y, marker='.', c=color_list)
        # print(len(self.traj))
        # self.traj = self.ax.plot(plot_x, plot_y, marker='.', colors="red")
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

    def add_zoom_func(self, base_scale=1.5):
        def zoom_func(event):
            bbox = self.ax.get_window_extent()
            if not(bbox.x0 < event.x < bbox.x1):
                return
            if not(bbox.y0 < event.y < bbox.y1):
                return
            if event.xdata is None or event.ydata is None:
                return
            cur_xlim = self.ax.get_xlim()
            cur_ylim = self.ax.get_ylim()
            cur_xrange = (cur_xlim[1] - cur_xlim[0]) * .5
            cur_yrange = (cur_ylim[1] - cur_ylim[0]) * .5
            xdata = event.xdata  # get event x location
            ydata = event.ydata  # get event y location
            # print(event.button, event.x, event.y, event.xdata, event.ydata)
            if event.button == 'up':
                # deal with zoom in
                scale_factor = base_scale
            elif event.button == 'down':
                # deal with zoom out
                scale_factor = 1 / base_scale
            else:
                # deal with something that should never happen
                scale_factor = 1
                # print(event.button)
            # set new limits
            xlim = [xdata - (xdata - cur_xlim[0]) / scale_factor,
                    xdata + (cur_xlim[1] - xdata) / scale_factor]
            ylim = [ydata - (ydata - cur_ylim[0]) / scale_factor,
                    ydata + (cur_ylim[1] - ydata) / scale_factor]

            self.ax.set_xlim(xlim)
            self.ax.set_ylim(ylim)

            if (abs(xlim[1] - xlim[0]) > self.img.shape[1]) and (abs(ylim[1] - ylim[0]) > self.img.shape[0]):
                self.ax.set_xlim([0, self.img.shape[1]])
                self.ax.set_ylim([self.img.shape[0], 0])

            self.figure.canvas.draw()
        self.figure.canvas.mpl_connect('scroll_event', zoom_func)
