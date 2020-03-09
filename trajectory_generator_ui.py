# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'trajectory_generator.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton,QComboBox,QListView,QLabel
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import random

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(944, 561)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(0, 370, 581, 131))
        self.textBrowser.setObjectName("textBrowser")
        self.m = PlotCanvas(self, width=5.81, height=3.61)
        self.m.move(0,0)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(590, 480, 94, 32))
        self.pushButton.setObjectName("pushButton")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(590, 0, 351, 361))
        self.groupBox.setObjectName("groupBox")
        self.tableView = QtWidgets.QTableView(self.groupBox)
        self.tableView.setGeometry(QtCore.QRect(20, 20, 321, 331))
        self.tableView.setObjectName("tableView")
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(590, 360, 231, 121))
        self.groupBox_2.setObjectName("groupBox_2")
        self.label = QtWidgets.QLabel(self.groupBox_2)
        self.label.setGeometry(QtCore.QRect(20, 30, 71, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setGeometry(QtCore.QRect(20, 60, 71, 16))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setGeometry(QtCore.QRect(20, 90, 71, 16))
        self.label_3.setObjectName("label_3")
        self.lineEdit = QtWidgets.QLineEdit(self.groupBox_2)
        self.lineEdit.setGeometry(QtCore.QRect(100, 30, 71, 21))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.groupBox_2)
        self.lineEdit_2.setGeometry(QtCore.QRect(100, 60, 71, 21))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_3 = QtWidgets.QLineEdit(self.groupBox_2)
        self.lineEdit_3.setGeometry(QtCore.QRect(100, 90, 71, 21))
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.label_4 = QtWidgets.QLabel(self.groupBox_2)
        self.label_4.setGeometry(QtCore.QRect(180, 30, 41, 20))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.groupBox_2)
        self.label_5.setGeometry(QtCore.QRect(180, 60, 41, 20))
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.groupBox_2)
        self.label_6.setGeometry(QtCore.QRect(180, 90, 41, 20))
        self.label_6.setObjectName("label_6")
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_3.setGeometry(QtCore.QRect(820, 360, 121, 121))
        self.groupBox_3.setObjectName("groupBox_3")
        self.radioButton_4 = QtWidgets.QRadioButton(self.groupBox_3)
        self.radioButton_4.setGeometry(QtCore.QRect(10, 30, 100, 20))
        self.radioButton_4.setObjectName("radioButton_4")
        self.radioButton_5 = QtWidgets.QRadioButton(self.groupBox_3)
        self.radioButton_5.setGeometry(QtCore.QRect(10, 60, 100, 20))
        self.radioButton_5.setObjectName("radioButton_5")
        self.radioButton_6 = QtWidgets.QRadioButton(self.groupBox_3)
        self.radioButton_6.setGeometry(QtCore.QRect(10, 90, 100, 20))
        self.radioButton_6.setObjectName("radioButton_6")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setEnabled(True)
        self.pushButton_2.setGeometry(QtCore.QRect(690, 480, 113, 32))
        self.pushButton_2.setDefault(False)
        self.pushButton_2.setObjectName("pushButton_2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 944, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "軌跡生成"))
        self.groupBox.setTitle(_translate("MainWindow", "制御点"))
        self.groupBox_2.setTitle(_translate("MainWindow", "制約条件"))
        self.label.setText(_translate("MainWindow", "制御周期"))
        self.label_2.setText(_translate("MainWindow", "最高速度"))
        self.label_3.setText(_translate("MainWindow", "最高加速度"))
        self.label_4.setText(_translate("MainWindow", "Hz"))
        self.label_5.setText(_translate("MainWindow", "m/s"))
        self.label_6.setText(_translate("MainWindow", "m/s^2"))
        self.groupBox_3.setTitle(_translate("MainWindow", "補間方法"))
        self.radioButton_4.setText(_translate("MainWindow", "等間隔"))
        self.radioButton_5.setText(_translate("MainWindow", "台形加速"))
        self.radioButton_6.setText(_translate("MainWindow", "躍度最小"))
        self.pushButton_2.setText(_translate("MainWindow", "データ出力"))

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
        cid = fig.canvas.mpl_connect('button_press_event', self.onclick)


    def plot(self):
        data1 = [random.random() for i in range(100)]
        data2 = [0.1*random.random() for i in range(100)]
        ax = self.figure.add_subplot(111)
        ax.plot(data1, 'ro')
        ax.plot(data2, 'b-')
        img = mpimg.imread('map.png')
        ax.imshow(img)
        ax.set_xticks([])
        ax.set_yticks([])
        self.draw()

    def onclick(self, event):
        print ('(%f, %f) [px]' %(event.xdata, event.ydata))
        origin = [82, 577]      # [px]
        scale = 0.00512295081   # 縮尺[m/px]
        point = [0, 0]
        point[0] = resizeByScale(event.xdata, scale, origin[0])
        point[1] = resizeByScale(-event.ydata, scale, -origin[1])

        data1 = [random.random() for i in range(100)]
        ax = self.figure.axes[0]
        ax.plot(event.xdata, event.ydata, marker='.')
        self.draw()
        print(self.figure.axes)


