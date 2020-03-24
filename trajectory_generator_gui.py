import sys

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton,QComboBox,QListView,QLabel,QTableWidgetItem
from PyQt5.QtGui import QIcon
from trajectory_generator_ui import Ui_MainWindow


class TrajectoryGeneratorGui(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(TrajectoryGeneratorGui, self).__init__(parent)
        self.setupUi(self)

    @pyqtSlot()
    def button_generate_Click(self):
        self.canvas.drawTrajectory()

    def button_export_Click(self):
        print(self)

    def button_cell_up_Click(self):
        current_row = self.tableWidget.currentRow()
        self.exchangeTalbeRow(current_row - 1, current_row)

    def button_cell_down_Click(self):
        current_row = self.tableWidget.currentRow()
        self.exchangeTalbeRow(current_row + 1, current_row)

    def cell_changed(self):
        self.updateControlPointsByTable()
        self.canvas.drawControlPoint(self.pm.control_points)

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

if __name__ == '__main__':
    argvs = sys.argv
    app = QApplication(argvs)
    trajectory_generator_gui = TrajectoryGeneratorGui()
    trajectory_generator_gui.show()
    sys.exit(app.exec_())

