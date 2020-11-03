import sys
import os
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton,QComboBox,QListView,QLabel,QTableWidgetItem, QFileDialog
from PyQt5.QtGui import QIcon
from trajectory_generator_ui import Ui_MainWindow
import numpy as np
import json
from collections import OrderedDict
import MinimumJerkModel
import TrajectoryCalculator
import GraphViewer
import PlotCanvas

import matplotlib.pyplot as plt

class TrajectoryGeneratorGui(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(TrajectoryGeneratorGui, self).__init__(parent)
        self.setupUi(self)

        # matplotlibの領域を描画
        self.canvas = PlotCanvas.PlotCanvas(self, width=4.5, height=6.80)
        self.canvas.move(10, 10)

        # 設定ファイルに書き込まれるパラメータ辞書
        self.app_param = {'hz': '1', 'max_speed': '0.22', 'max_acc': '1000'}

        # 経路計算機
        self.tc = TrajectoryCalculator.TrajectoryCalculator()
        self.via_point = [] # 経由点の座標リスト
        self.via_speed = [] # 経由点での司令速度リスト


    @pyqtSlot()
    def button_generate_Click(self):
        self.textBrowser.append("経路生成開始")

        # 制約条件の設定
        try:
            self.tc.setDotGap(float(self.lineEdit_8.text()))
            self.tc.setFrequency(float(self.lineEdit.text()))
            self.tc.setMaxLinearSpeed(float(self.lineEdit_2.text()))
            self.tc.setMaxLinearAcceleration(float(self.lineEdit_3.text()))
            # self.tc.setMaxAngularSpeed(float(self.lineEdit_3.text()))
        except ValueError:
            self.textBrowser.append("制約条件の入力値が不正です")
            self.redraw()
            return

        # 経由点の座標と速度を設定
        self.tc.setViaPoint(np.array(self.via_point))
        self.tc.setViaSpeed(self.via_speed)

        # 計算
        self.tc.calculate()

        # 結果表示
        self.textBrowser.append("------------")
        self.textBrowser.append("経路生成終了")
        self.textBrowser.append("経路長　" + '{0:.3f}'.format(self.tc.getTrajectoryLength()) + "[m]")
        self.textBrowser.append("到達時間" + '{0:.3f}'.format(self.tc.getExpectedTime()) + "[s]")

        # 描画
        self.canvas.drawTrajectory(self.tc.getTrajectory(), self.tc.getSpeedProfileProfile())
        self.redraw()


    def redraw(self):
        self.resize(self.width(), self.height()+1)
        self.resize(self.width(), self.height()-1)


    # ファイル保存
    def button_export_Click(self):
        # 保存時の拡張子を取得
        extension = ""
        if self.comboBox.currentIndex() == 0:
            extension = "csv"
        else:
            extension = "py"

        # 保存先の取得
        fname, selectedFilter = QFileDialog.getSaveFileName(self, 'ファイルの保存', 'trajectory.' + extension)
        if fname == "":
            return

        # 書き込むテキストの生成
        write_text = ""
        if self.comboBox.currentIndex() == 0:
            for i in range(len(self.tc.getTrajectory())):
                write_text += str(self.tc.getTrajectory()[i][0])
                write_text += ","
                write_text += str(self.tc.getTrajectory()[i][1])
                write_text += ","
                write_text += "0"
                write_text += ","
                write_text += str(self.tc.getSpeedProfileProfile()[i])
                write_text += "\n"
        else:
            write_text = "["
            for i in range(len(self.tc.getTrajectory())):
                write_text += "["
                write_text += str(self.tc.getTrajectory()[i][0])
                write_text += ","
                write_text += str(self.tc.getTrajectory()[i][1])
                write_text += "]"
                if i != len(self.tc.getTrajectory()) - 1:
                    write_text += ","
            write_text += "]"

        # 書き込み
        self.saveFile(fname, write_text)
        self.redraw()

    # セルを一つ上に
    def button_cell_up_Click(self):
        current_row = self.tableWidget.currentRow()
        self.exchangeTalbeRow(current_row - 1, current_row)
        self.redraw()

    # セルを一つ下に
    def button_cell_down_Click(self):
        current_row = self.tableWidget.currentRow()
        self.exchangeTalbeRow(current_row + 1, current_row)
        self.redraw()

    # tableの変更イベント
    def cell_changed(self):
        # tableの値をpointmanagerに書き込む
        self.updateControlPointsByTable()
        # 制御点を再描画
        self.canvas.drawControlPoint(self.via_point)
        # self.redraw()

    def button_cell_add_Click(self):
        self.textBrowser.append("未実装")
        self.redraw()

    def button_cell_delete_Click(self):
        current_row = self.tableWidget.currentRow()
        self.via_point.pop(current_row)
        self.tableWidget.removeRow(current_row)
        self.canvas.drawControlPoint(self.via_point)
        self.redraw()

    def button_select_settingfile(self):
        fname, selectedFilter = QFileDialog.getOpenFileName(self, 'ファイルの保存', 'setting.json')
        # fname = os.path.dirname(__file__) + "/min.json"

        with open(fname) as f:
            self.app_param = json.load(f)

        # 各lineEdit，tableに反映
        self.lineEdit.setText(self.app_param['hz'])
        self.lineEdit_2.setText(self.app_param['max_speed'])
        self.lineEdit_3.setText(self.app_param['max_acc'])
        self.lineEdit_4.setText(fname)
        self.via_point = self.app_param['cp']

        # tableをクリアし，座標の数だけ行を用意
        items = self.via_point
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(len(items))

        # tableへの書き込み
        r = 0
        for item in items:
            self.tableWidget.setItem(r, 0, QTableWidgetItem('{0:.3f}'.format(item[0])))
            self.tableWidget.setItem(r, 1, QTableWidgetItem('{0:.3f}'.format(item[1])))
            r += 1

        self.redraw()


    # 設定ファイルのエクスポート
    def button_export_settingfile(self):
        self.app_param['hz'] = self.lineEdit.text()
        self.app_param['max_speed'] = self.lineEdit_2.text()
        self.app_param['max_acc'] = self.lineEdit_3.text()
        self.app_param['cp'] = self.via_point

        # 保存先の取得
        fname, selectedFilter = QFileDialog.getSaveFileName(self, 'ファイルの保存', 'setting.json')
        # 辞書型をjsonの文字列に変換
        write_text = json.dumps(self.app_param)
        # 書き込み
        self.saveFile(fname, write_text)
        self.redraw()

    def button_open_map(self):
        self.textBrowser.append("未実装")
        self.redraw()

    def button_adjust_origin(self):
        point = [0, 0]
        point[0] = float(self.lineEdit_6.text())
        point[1] = float(self.lineEdit_7.text())
        self.canvas.drawOrigin(point)
        self.redraw()

    def button_curvature_check(self):
        # print(self.tc.getTrajectoryLengthList())
        # print(self.tc.getCurvature())
        # print(len(self.tc.getTrajectoryLengthList()))
        # print(len(self.tc.getCurvature()))
        gv = GraphViewer.GraphViewer()
        gv.displayCurvatureProfile(self.tc.getTrajectoryLengthList(), self.tc.getCurvature())
        self.redraw()

    def button_speed_check(self):
        gv = GraphViewer.GraphViewer()
        gv.displaySpeedProfile(self.tc.getTimeStamp(), self.tc.getSpeedProfileProfile())
        self.redraw()

    def button_acceleration_check(self):
        gv = GraphViewer.GraphViewer()
        gv.displayAccelerationProfile(self.tc.getTimeStamp(), self.tc.getAccelerationProfile())
        self.redraw()

    # tableの行を入れ替える
    def exchangeTalbeRow(self, row1, row2):
        for col in range(self.tableWidget.columnCount()):
                temp = self.tableWidget.takeItem(row1, col)
                self.tableWidget.setItem(row1, col, self.tableWidget.takeItem(row2, col))
                self.tableWidget.setItem(row2, col, temp)
        self.tableWidget.setCurrentCell(row1, self.tableWidget.currentColumn())

    # tableの値をpointmanagerに書き込む
    def updateControlPointsByTable(self):
        table_data_list = []
        for row in range(self.tableWidget.rowCount()):
            row_data = []
            for column in range(4):
                # 各要素を読み込み
                try:
                    item_str = self.tableWidget.item(row, column).text()
                except AttributeError:
                    return -1

                try:
                    item_float = float(item_str)
                except ValueError:
                    return -1
                row_data.append(item_float)
            table_data_list.append(row_data)

        self.via_point = []
        self.via_speed = []
        for item in table_data_list:
            self.via_point.append([item[0], item[1]])
            self.via_speed.append(item[3])


    def saveFile(self, name, text):
        with open(name, mode='w') as f:
            f.write(text)

if __name__ == '__main__':
    argvs = sys.argv
    app = QApplication(argvs)
    trajectory_generator_gui = TrajectoryGeneratorGui()
    trajectory_generator_gui.show()
    sys.exit(app.exec_())

