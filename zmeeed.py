from PyQt5.QtWidgets import *
import sys
import json


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("zmeeed")
        self.move(300, 300)
        self.resize(200, 200)

        with open("out.json") as f:
            data = json.load(f)

        self.blocks = []

        y = 30

        for block in data['blocks']:
            block_text = ''
            for op in block['code']:
                offset, opname, argval = op['offset'], op['opname'], op['argval']
                block_text += f'<font color="gray">{offset:0>3}:</font> <font color="blue">{opname}</font> {argval}<br/>'


            lbl = QLabel(block_text, self)
            lbl.setStyleSheet('font-family: monospace')
            lbl.adjustSize()
            lbl.move(30, y)

            print(dir(lbl.size()))


            self.blocks.append(lbl)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
