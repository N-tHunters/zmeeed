from PyQt5.QtWidgets import *
from PyQt5.QtCore import QPoint, QEvent, Qt
from PyQt5.QtGui import QPainter, QPen
import html


class ConstsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setupUi()

    def setupUi(self):
        self.no_bytecode_lbl = QLabel('No bytecode to analyze. Please pick one from File menu.', self)
        self.no_bytecode_lbl.move(20, 20)

        self.consts = []

        if self.parent.analyzer is not None:
            self.buildView()

    def buildView(self):
        self.no_bytecode_lbl.hide()
        for const in self.consts:
            const.hide()
            del const
        self.consts = []

        x = 10
        y = 10

        for i, const in enumerate(self.parent.analyzer.bytecode_analyzer.data['consts']):
            const_text = f'<font color="gray">{i:0>3}:</font> {const[0]} (<font color="blue">{const[1]}</font>)'
            lbl = QLabel(const_text, self)
            lbl.setStyleSheet('font-family: monospace')
            lbl.adjustSize()
            lbl.move(x, y)
            y += lbl.height() + 5
            self.consts.append(lbl)
