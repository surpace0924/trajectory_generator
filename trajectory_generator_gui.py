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
        self.tableWidget.clear()
        items = [['hoge', 'HOGE'], ['fuga', 'FUGA'], ['piyo', 'PIYO']]

        self.tableWidget.setRowCount(len(items))
        self.tableWidget.setColumnCount(4);

        r = 0
        for item in items:
            self.tableWidget.setItem(r, 0, QTableWidgetItem(item[0]))
            self.tableWidget.setItem(r, 1, QTableWidgetItem(item[1]))
            r += 1

        print(self)

    def button_export_Click(self):
        print(self)


if __name__ == '__main__':
    argvs = sys.argv
    app = QApplication(argvs)
    trajectory_generator_gui = TrajectoryGeneratorGui()
    trajectory_generator_gui.show()
    sys.exit(app.exec_())

