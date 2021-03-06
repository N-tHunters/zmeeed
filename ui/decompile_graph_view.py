from PyQt5.QtWidgets import *
from PyQt5.QtCore import QPoint, QEvent, Qt
from PyQt5.QtGui import QPainter, QPen
import html
import json




class DecompileBlock(QLabel):
    def __init__(self, code, parent=None):
        self.code = code
        self.links_in = []
        self.links_out = []

        block_text = ''
        for inst in self.code:
            block_text += inst + '<br/>'

        super().__init__(block_text, parent)
        self.setStyleSheet('font-family: monospace; border: 1px solid gray; padding: 5px')
        self.adjustSize()
        self.installEventFilter(parent)
        self.show()


class DecompileGraphView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setupUi()

    def setupUi(self):
        self.setGeometry(0, 40, self.parent.width(), self.parent.height() - 40)
        self.dragStartPos = None

        self.blocks = []
        self.links = []

        self.no_bytecode_lbl = QLabel('No bytecode to analyze. Please pick one from File menu.', self)
        self.no_bytecode_lbl.move(20, 20)

        if self.parent.analyzer is not None:
            self.buildView()

    def buildView(self):
        self.no_bytecode_lbl.hide()

        for block in self.blocks:
            block.hide()
            del block
        self.blocks = []
        self.links = []

        y = 30
        x = self.width() // 2

        analyzer = self.parent.analyzer.decompiler

        for block in analyzer.data['blocks']:
            block = DecompileBlock(block, self)
            self.blocks.append(block)

        self.graph = dict()

        for jump in self.parent.analyzer.bytecode_analyzer.data['jumps']:
            from_block, to_block = jump[0]
            self.blocks[from_block].links_out.append(to_block)
            self.blocks[to_block].links_in.append(to_block)
            self.links.append((from_block, to_block, [Qt.red, Qt.blue, Qt.green][1+jump[1]], len(self.graph.get(from_block, []))))
            if self.graph.get(from_block) is None:
                self.graph[from_block] = []
            self.graph[from_block].append(to_block)

        queue = [(0, 0)]
        used = [False for i in range(len(self.blocks))]
        used[0] = True
        self.block_strata = [0 for i in range(len(self.blocks))]
        strata_blocks = dict()
        strata_max_height = dict()

        while len(queue) != 0:
            block, strata = queue[0]
            self.block_strata[block] = strata
            queue.pop(0)

            strata = self.block_strata[block]
            if strata_blocks.get(strata) is None:
                strata_blocks[strata] = []
            strata_blocks[strata].append((block, self.blocks[block]))

            if strata_max_height.get(strata) is None:
                strata_max_height[strata] = 0
            strata_max_height[strata] = max(strata_max_height[strata], self.blocks[block].height())
            for child in self.graph.get(block, []):
                if not used[child]:
                    used[child] = True
                    queue.append((child, strata + 1))

        strata_height = [y]
        for strata in range(1, len(strata_max_height)):
            strata_height.append(strata_height[-1] + 30 + strata_max_height[strata-1])

        for strata in range(len(strata_max_height)):
            sum_width = 0
            for i, block in strata_blocks[strata]:
                sum_width += block.width()
            sum_width += 30 * (len(strata_blocks[strata]) - 1)
            sum_width //= 2
            for i, block in strata_blocks[strata]:
                block.move(x - sum_width, y + strata_height[self.block_strata[i]])
                sum_width -= 30 + block.width()

        self.update()


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        for i, link in enumerate(self.links):
            painter.setPen(QPen(link[2], 2, Qt.SolidLine, Qt.SquareCap, Qt.BevelJoin))
            if self.block_strata[link[0]] < self.block_strata[link[1]]:
                link_start_block = self.blocks[link[0]]
                link_start_pos = link_start_block.pos() + \
                    QPoint(link_start_block.width() // 2, link_start_block.height())
                link_start_pos += QPoint(link[3] * 4, 0)
                link_end_block = self.blocks[link[1]]
                link_end_pos = link_end_block.pos() + QPoint(link_end_block.width() // 2, 0)
                midY = (link_end_pos.y() + link_start_pos.y()) // 2 + link[3] * 4
                painter.drawLine(link_start_pos, QPoint(link_start_pos.x(), midY))
                painter.drawLine(QPoint(link_start_pos.x(), midY), QPoint(link_end_pos.x(), midY))
                painter.drawLine(QPoint(link_end_pos.x(), midY), link_end_pos)
            else:
                link_start_block = self.blocks[link[0]]
                link_start_pos = link_start_block.pos() + \
                    QPoint(link_start_block.width() // 2, link_start_block.height())
                link_start_pos += QPoint(link[3] * 4, 0)
                link_end_block = self.blocks[link[1]]
                link_end_pos = link_end_block.pos() + QPoint(link_end_block.width() // 2 - 10, 0)
                painter.drawLine(link_start_pos,
                                 QPoint(link_start_pos.x(), link_start_pos.y() + 5 + link[3] * 4))
                painter.drawLine(QPoint(link_start_pos.x(), link_start_pos.y() + 5 + link[3] * 4),
                                 QPoint(link_start_pos.x() + link_start_block.width() // 2 + 5, link_start_pos.y() + 5 + link[3] * 4))
                painter.drawLine(QPoint(link_start_pos.x() + link_start_block.width() // 2 + 5, link_start_pos.y() + 5 + link[3] * 4),
                                 QPoint(link_start_pos.x() + link_start_block.width() // 2 + 5, link_end_pos.y() - 5))
                painter.drawLine(QPoint(link_start_pos.x() + link_start_block.width() // 2 + 5, link_end_pos.y() - 5),
                                 QPoint(link_end_pos.x(), link_end_pos.y() - 5))
                painter.drawLine(QPoint(link_end_pos.x(), link_end_pos.y() - 5), link_end_pos)

    def dragGraph(self, dx, dy):
        for lbl in self.blocks:
            lbl.move(lbl.pos().x() + dx, lbl.pos().y() + dy)
        self.update()

    def mousePressEvent(self, event):
        self.dragStartPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.dragStartPos is None:
            return
        relativeDrag = event.globalPos() - self.dragStartPos
        self.dragStartPos = event.globalPos()
        self.dragGraph(relativeDrag.x(), relativeDrag.y())

    def mouseReleaseEvent(self, event):
        self.dragStartPos = None

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            self.mousePressEvent(event)
        if event.type() == QEvent.MouseMove:
            self.mouseMoveEvent(event)
        if event.type() == QEvent.MouseButtonRelease:
            self.mouseReleaseEvent(event)
        return super(QWidget, self).eventFilter(obj, event)
