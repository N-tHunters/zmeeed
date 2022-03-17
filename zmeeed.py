from PyQt5.QtWidgets import *
from PyQt5.QtCore import QPoint, QEvent, Qt
from PyQt5.QtGui import QPainter, QPen
import sys
import json


from ui.bytecode_graph_view import BytecodeGraphView


class PycAnalyzer:
    def __init__(self, filename):
        self.filename = filename


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.analyzer = None
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("zmeeed")
        self.setGeometry(QDesktopWidget().screenGeometry())

        exitAction = QAction('&Exit', self)
        exitAction.triggered.connect(qApp.quit)


        openAction = QAction('&Open', self)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)

        self.tabs = QTabWidget(self)
        self.tabs.move(0, 20)
        self.tabs.resize(self.width(), self.height() - 40)

        bGraphView = BytecodeGraphView(self)
        dGraphView = BytecodeGraphView(self)
        constsView = ConstsView(self)
        self.tabs.addTab(bGraphView, "b graph")
        self.tabs.addTab(dGraphView, "d graph")
        self.tabs.addTab(constsView, "consts")


class ConstsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        pass



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
