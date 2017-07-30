import sys, re
from PyQt5.QtWidgets import (
    QMessageBox, QApplication, QAction,
    QWidget, QMainWindow, QToolTip, QPushButton,
    QDesktopWidget, QFileDialog, QInputDialog
    )
from PyQt5.QtGui import QIcon, QFont
from logview import LogView


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
        self.openAction.triggered.connect(self.openLog)

        self.exitAction = QAction(QIcon(
            'icons/application-exit.png'),
            'E&xit',
            self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip('Exit this application.')
        self.exitAction.triggered.connect(self.close)

        self.watchAction = QAction(
            QIcon('icons/edit-find.png'),
            '&Watch for...',
            self)
        self.watchAction.setShortcut('Ctrl+W')
        self.watchAction.setStatusTip(
            'Watch the log file for occurences of a particular string.')
        self.watchAction.triggered.connect(self.watchFor)

        self.aboutAction = QAction(
            QIcon('icons/help-about.png'),
            '&About',
            self)
        self.aboutAction.setStatusTip('About this application.')
        self.aboutAction.triggered.connect(self.showAbout)

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

        self.logView = LogView([], [])
        self.setCentralWidget(self.logView)

        self.pattern = ''  # pattern to be matched
        # explicitly define this since
        # we'll be testing for it later
        self.fileContents = ''

        self.resize(400, 500)
        self.setWindowTitle('LogWatch')
        self.setWindowIcon(QIcon('icons/edit-paste.png'))
        self.show()

    def closeEvent(self, event):

        reply = QMessageBox.question(
            self,
            'You sure?',
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

    def openLog(self, event):
        fname = QFileDialog.getOpenFileName(
            self,
            'Choose a log file',
            '/var/log')
        if fname[0]:
            self.logFile = fname[0]
            f = open(fname[0], 'r')
            with f:
                self.fileContents = f.read()
                self.statusBar().showMessage('Log file loaded!')
                self.updateLogView()
        else:
            self.statusBar().showMessage('Please select a log file!')

    def watchFor(self, event):
        text, ok = QInputDialog.getText(
            self,
            'Input pattern',
            'Regular Expression Pattern to match: ')
        if ok:
            # error checking
            try:
                re.search(str(text), "Hello, World")
            except Exception as e:
                self.statusBar().showMessage("Error: " + str(e))
                return
            self.pattern = str(text)
            self.updateLogView()
            self.statusBar().showMessage("Matching: " + self.pattern)

    def updateLogView(self):
        if not self.pattern:
            self.fileContentsList = self.fileContents.split('\n')
            self.fileLineNumbers = []
            for i in range(0, len(self.fileContentsList)):
                self.fileLineNumbers.append(i + 1)
            self.logView.updateContents(
                self.fileContentsList, self.fileLineNumbers)
        else:
            if not self.fileContents:
                return
            contentsList = self.fileContents.split('\n')
            self.fileContentsList = []
            self.fileLineNumbers = []
            for i in range(0, len(contentsList)):
                try:
                    if (re.search(self.pattern, contentsList[i])):
                        self.fileContentsList.append(contentsList[i])
                        self.fileLineNumbers.append(i + 1)
                except Exception as e:
                    self.statusBar().showMessage("Error: " + str(e))
                    self.fileContentsList = []
                    self.fileLineNumbers = []
                    return
            self.statusBar().showMessage(
                "Matched " + str(len(self.fileContentsList)) + " occurences!")
            self.logView.updateContents(
                self.fileContentsList, self.fileLineNumbers)

    def showAbout(self, event):
        QMessageBox.about(self, "About", """
            <h2>LogWatch</h2>
            <p><i>v0.0.1</i></p>
            <p>A simple program that does what the name says.</p>
            <p>MIT License. Made with &lt;3,
                <a href="https://www.riverbankcomputing.com/software/pyqt/download5">
                    PyQt5
                </a>, 
                <a href="https://qt.io">
                    Qt5
                </a> and 
                <a href="https://python.org">
                Python
                </a>.
            </p>
            <p>Icons from: 
                <a href="https://www.gnome-look.org/p/1167936/">
                    https://www.gnome-look.org/p/1167936/
                </a>
            </p>
            """)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    lgw = LogWatchWindow()
    sys.exit(app.exec_())
