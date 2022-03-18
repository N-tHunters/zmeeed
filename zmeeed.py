from PyQt5.QtWidgets import *
from PyQt5.QtCore import QPoint, QEvent, Qt
from PyQt5.QtGui import QPainter, QPen
import sys
import json


from ui.bytecode_graph_view import BytecodeGraphView
from ui.consts_view import ConstsView

from bytecode_analyzer import BytecodeAnalyzer
from decompiler import Decompiler


class PycAnalyzer:
    def __init__(self, filename):
        self.filename = filename
        self.bytecode_analyzer = BytecodeAnalyzer(filename)
        self.decompiler = Decompiler(self.bytecode_analyzer)

    def analyze(self):
        self.bytecode_analyzer.analyze()
        self.decompiler.decompile()


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


        openAction = QAction('&Open and analyze', self)
        openAction.triggered.connect(self.openAndAnalyze)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)

        self.tabs = QTabWidget(self)
        self.tabs.move(0, 20)
        self.tabs.resize(self.width(), self.height() - 40)

        self.bGraphView = BytecodeGraphView(self)
        self.constsView = ConstsView(self)
        self.tabs.addTab(self.bGraphView, "b graph")
        self.tabs.addTab(self.constsView, "consts")

    def openAndAnalyze(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Pick a pyc", "", "Python Bytecode (*.pyc)", options=options)
        if fileName:
            self.analyzer = PycAnalyzer(fileName)
            self.analyzer.analyze()
            self.bGraphView.buildView()
            self.constsView.buildView()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
