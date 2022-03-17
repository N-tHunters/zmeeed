from PyQt5.QtWidgets import *
import sys
import json
import html


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("zmeeed")

        with open("out.json") as f:
            data = json.load(f)

        self.blocks = []

        y = 30

        for block in data['blocks']:
            block_text = ''
            for op in block['code']:
                offset, opname, argval = op['offset'], op['opname'], op['argval']
                argval = html.escape(argval)
                block_text += f'<font color="gray">{offset:0>3}:</font> <font color="blue">{opname}</font> {argval}<br/>'

            lbl = QLabel(block_text, self)
            lbl.setStyleSheet('font-family: monospace')
            lbl.adjustSize()
            lbl.move(30, y)

            y += 30 + lbl.height()

            self.blocks.append(lbl)

    def keyPressEvent(self, event):
        if event.key() == ord('J'):
            for lbl in self.blocks:
                lbl.move(lbl.pos().x(), lbl.pos().y() - 10)
        if event.key() == ord('K'):
            for lbl in self.blocks:
                lbl.move(lbl.pos().x(), lbl.pos().y() + 10)
        if event.key() == ord('H'):
            for lbl in self.blocks:
                lbl.move(lbl.pos().x() + 10, lbl.pos().y())
        if event.key() == ord('L'):
            for lbl in self.blocks:
                lbl.move(lbl.pos().x() - 10, lbl.pos().y())




if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
