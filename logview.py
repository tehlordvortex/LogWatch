# adapted from http://doc.qt.io/qt-5/qtwidgets-widgets-codeeditor-example.html

from PyQt5.QtWidgets import QPlainTextEdit, QTextEdit
from PyQt5.QtCore import Qt, QRect, pyqtSignal
from PyQt5.QtGui import QTextFormat, QPainter, QColor
from numbergutter import NumberGutter


class LogView(QPlainTextEdit):

    """
    A widget that displays the contents of the log file
    """
    updateContentSignal = pyqtSignal(list, list)

    def __init__(self, contents, lineNumbers):
        super().__init__()
        self.gutter = NumberGutter(self)
        self.dirty = False

        self.contents = contents
        self.lineNumbers = lineNumbers
        self.setPlainText('\n'.join(self.contents))
        self.setReadOnly(True)
        # self.setTextInteractionFlags(
        #     self.textInteractionFlags() | Qt.
        #     TextInteractionFlags.TextSelectableByKeyboard)

        self.blockCountChanged.connect(self.updateGutterAreaWidth)
        self.updateRequest.connect(self.updateGutterArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateContentSignal.connect(self.updateContents)

        self.updateGutterAreaWidth(0)
        self.highlightCurrentLine()

    def updateContents(self, contents, lineNumbers):
        self.contents = contents
        self.lineNumbers = lineNumbers
        self.setPlainText('\n'.join(self.contents))
        if self.isVisible():
            self.repaint()
        else:
            #self.setAttribute(Qt.WA_DontShowOnScreen)
            #self.show()
            self.dirty = True
            #self.hide()
            #self.setAttribute(Qt.WA_DontShowOnScreen, false)

    def gutterAreaWidth(self):
        if (len(self.lineNumbers) > 0):

            maxN = max(self.lineNumbers)
            digits = len(str(maxN))

            space = 3 + self.fontMetrics().width('9') * digits

            return space
        else:
            return 3 + self.fontMetrics().width('9')

    def updateGutterAreaWidth(self, newBlockCount):
        self.setViewportMargins(self.gutterAreaWidth(), 0, 0, 0)

    def updateGutterArea(self, rect, dy):
        if dy:
            self.gutter.scroll(0, dy)
        else:
            self.gutter.update(0, rect.y(), self.gutter.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateGutterAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        cr = self.contentsRect()
        self.gutter.setGeometry(
            QRect(cr.left(), cr.top(), self.gutterAreaWidth(), cr.height()))

    def showEvent(self, event):
        super().showEvent(event)

        if self.dirty:
            self.repaint()
            self.dirty = False

    def highlightCurrentLine(self):
        extraSelections = []

        selection = QTextEdit.ExtraSelection()
        lineColor = QColor(Qt.yellow).lighter(160)

        selection.format.setBackground(lineColor)
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        extraSelections.append(selection)

        self.setExtraSelections(extraSelections)

    def gutterPaintEvent(self, event):
        # fill out  rect for the gutter
        painter = QPainter(self.gutter)
        painter.fillRect(event.rect(), Qt.lightGray)
        if (len(self.lineNumbers) < 1):
            return
        # each line is a block,
        # so we get the first visible block then loop over the rest
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(
            self.blockBoundingGeometry(block).
            translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.setPen(Qt.black)
                painter.drawText(
                    0,
                    top,
                    self.gutter.width(),
                    self.fontMetrics().height(),
                    Qt.AlignRight,
                    str(self.lineNumbers[blockNumber]))
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1



