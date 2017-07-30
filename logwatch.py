import sys
from PyQt5.QtWidgets import (
    QMessageBox, QApplication, qApp, QAction,
    QWidget, QMainWindow, QToolTip, QPushButton,
    QDesktopWidget
    )
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QCoreApplication


class LogWatchWindow(QMainWindow):

    """docstring for Example"""

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        QToolTip.setFont(QFont('SansSerif', 10))

        self.statusBar().showMessage('Ready')

        self.openAction = QAction(
            QIcon('icons/document-open.png'),
            '&Open Log',
            self)
        self.openAction.setShortcut('Ctrl+O')
        self.openAction.setStatusTip(
            'Open a log file for watching and analysis.')

        self.exitAction = QAction(QIcon(
            'icons/application-exit.png'),
            'E&xit',
            self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip('Exit this application.')
        self.exitAction.triggered.connect(qApp.quit)

        self.watchAction = QAction(
            QIcon('icons/edit-find.png'),
            '&Watch for...',
            self)
        self.watchAction.setShortcut('Ctrl+W')
        self.watchAction.setStatusTip(
            'Watch the log file for occurences of a particular string.')

        self.aboutAction = QAction(
            QIcon('icons/help-about.png'),
            '&About',
            self)
        self.aboutAction.setStatusTip('About this application.')

        self.menubar = self.menuBar()

        self.fileMenu = self.menubar.addMenu('&File')
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addAction(self.exitAction)

        self.toolsMenu = self.menubar.addMenu('&Tools')
        self.toolsMenu.addAction(self.watchAction)

        self.helpMenu = self.menubar.addMenu('&Help')
        self.helpMenu.addAction(self.aboutAction)

        self.toolbar = self.addToolBar('Search')
        self.toolbar.addAction(self.watchAction)

        self.resize(800, 600)
        self.center()
        self.setWindowTitle('LogWatch')
        self.setWindowIcon(QIcon('icons/edit-paste.png'))

        self.show()

    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'You sure?',
            'Are you sure you want to leave this awesome app?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def center(self):
        windowRect = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        windowRect.moveCenter(centerPoint)
        self.move(windowRect.topLeft())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    lgw = LogWatchWindow()
    sys.exit(app.exec_())
