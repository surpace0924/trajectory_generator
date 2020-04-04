import sys

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton,QComboBox,QListView,QLabel,QTableWidgetItem, QFileDialog
from PyQt5.QtGui import QIcon
from trajectory_generator_ui import Ui_MainWindow
import numpy as np
import CatmullRom


class TrajectoryGeneratorGui(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(TrajectoryGeneratorGui, self).__init__(parent)
        self.setupUi(self)

    @pyqtSlot()
    def button_generate_Click(self):
        self.textBrowser.append("経路生成開始")
        points = np.array(self.pm.control_points)
        cr = CatmullRom.CatmullRom()
        dots = []
        cr.setControlPoint(points)
        cr.hz = float(self.lineEdit.text())
        cr.max_speed = float(self.lineEdit_2.text())
        cr.max_acc = float(self.lineEdit_3.text())
        cr.calculate()
        dots, length, time = cr.getResult()
        self.pm.trajectory = dots
        self.textBrowser.append("経路生成終了")
        self.textBrowser.append("経路長　" + '{0:.3f}'.format(length) + "[m]")
        self.textBrowser.append("到達時間" + '{0:.3f}'.format(time) + "[s]")

        self.canvas.drawTrajectory(dots)
        self.redraw()

    def redraw(self):
        self.MainWindow.resize(self.MainWindow.width(), self.MainWindow.height()+1)
        self.MainWindow.resize(self.MainWindow.width(), self.MainWindow.height()-1)
        print(self.MainWindow.width())
        print(self.MainWindow.height())


    # ファイル保存
    def button_export_Click(self):
        # 保存先の取得
        fname, selectedFilter = QFileDialog.getSaveFileName(self, 'ファイルの保存', 'trajectory.csv')
        if fname == "":
            return

        # 書き込むテキストの生成
        write_text = "["
        for i in range(len(self.pm.trajectory)):
            write_text += "["
            write_text += str(self.pm.trajectory[i][0])
            write_text += ","
            write_text += str(self.pm.trajectory[i][1])
            write_text += "]"
            if i != len(self.pm.trajectory) - 1:
                write_text += ","
        write_text += "]"

        # 書き込み
        self.saveFile(fname, write_text)

    # セルを一つ上に
    def button_cell_up_Click(self):
        current_row = self.tableWidget.currentRow()
        self.exchangeTalbeRow(current_row - 1, current_row)

    # セルを一つ下に
    def button_cell_down_Click(self):
        current_row = self.tableWidget.currentRow()
        self.exchangeTalbeRow(current_row + 1, current_row)

    # tableの変更イベント
    def cell_changed(self):
        # tableの値をpointmanagerに書き込む
        self.updateControlPointsByTable()
        # 制御点を再描画
        self.canvas.drawControlPoint(self.pm.control_points)

    def button_cell_add_Click(self):
        self.textBrowser.append("未実装")

    def button_cell_delete_Click(self):
        self.textBrowser.append("未実装")

    # tableの行を入れ替える
    def exchangeTalbeRow(self, row1, row2):
        for col in range(self.tableWidget.columnCount()):
                temp = self.tableWidget.takeItem(row1, col);
                self.tableWidget.setItem(row1, col, self.tableWidget.takeItem(row2, col))
                self.tableWidget.setItem(row2, col, temp)
        self.tableWidget.setCurrentCell(row1, self.tableWidget.currentColumn())

    # tableの値をpointmanagerに書き込む
    def updateControlPointsByTable(self):
        buf_poses = []
        for row in range(self.tableWidget.rowCount()):
            row_data = []
            for column in range(2):
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
            buf_poses.append(row_data)
        self.pm.control_points = buf_poses


    def saveFile(self, name, text):
        with open(name, mode='w') as f:
            f.write(text)

if __name__ == '__main__':
    argvs = sys.argv
    app = QApplication(argvs)
    trajectory_generator_gui = TrajectoryGeneratorGui()
    trajectory_generator_gui.show()
    sys.exit(app.exec_())

