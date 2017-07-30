# adapted from http://doc.qt.io/qt-5/qtwidgets-widgets-codeeditor-example.html
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QSize


class NumberGutter(QWidget):

    """
    A gutter that provides line numbers.
    To be attached to LogView widget.
    """

    def __init__(self, logview):
        super().__init__(logview)
        self.logview = logview

    def sizeHint(self):
        return QSize(self.logview.gutterAreaWidth(), 0)

    def paintEvent(self, event):
        self.logview.gutterPaintEvent(event)
