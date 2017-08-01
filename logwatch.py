import sys, re
from PyQt5.QtWidgets import (
    QMessageBox, QApplication, QAction,
    QWidget, QMainWindow, QSystemTrayIcon,
    QDesktopWidget, QFileDialog, QInputDialog,
    QMenu
    )
from PyQt5.QtGui import QIcon, QFont, QTextCharFormat
from logview import LogView
from highlighter import HighlightRule, Highlighter
from PyQt5.QtCore import QRegularExpression, Qt
from watch import Watch


class LogWatchWindow(QMainWindow):

    """Custom QMainWindow for all the magic"""

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

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
            'Watch the log file for occurrences of a particular RegEx pattern')
        self.watchAction.triggered.connect(self.watchFor)

        self.refreshAction = QAction(
            QIcon('icons/view-refresh.png'),
            '&Refresh',
            self)
        self.refreshAction.setShortcut('F5')
        self.refreshAction.setStatusTip('Manually refresh teh log view')
        self.refreshAction.triggered.connect(self.refreshLogView)

        self.aboutAction = QAction(
            QIcon('icons/help-about.png'),
            '&About',
            self)
        self.aboutAction.setStatusTip('About this application.')
        self.aboutAction.triggered.connect(self.showAbout)

        self.minimizeToTrayAction = QAction(
            QIcon(''),
            '&Minimize to tray',
            self)
        self.minimizeToTrayAction.setShortcut('Ctrl+T')
        self.minimizeToTrayAction.setStatusTip('Minimizes to the system tray')
        self.minimizeToTrayAction.triggered.connect(self.minimizeToTray)

        self.showAction = QAction(
            QIcon(''),
            'Show Window',
            self)
        self.showAction.triggered.connect(self.showWindow)

        self.menubar = self.menuBar()

        self.fileMenu = self.menubar.addMenu('&File')
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addAction(self.minimizeToTrayAction)
        self.fileMenu.addAction(self.exitAction)

        self.toolsMenu = self.menubar.addMenu('&Tools')
        self.toolsMenu.addAction(self.watchAction)
        self.toolsMenu.addAction(self.refreshAction)

        self.helpMenu = self.menubar.addMenu('&Help')
        self.helpMenu.addAction(self.aboutAction)

        self.toolbar = self.addToolBar('Tools')
        self.toolbar.addAction(self.watchAction)
        self.toolbar.addAction(self.refreshAction)

        self.logView = LogView([], [])
        self.setCentralWidget(self.logView)

        self.trayIcon = QSystemTrayIcon(QIcon('icons/edit-paste.png'), self)
        self.trayIcon.setToolTip("Ready!")
        self.trayIconMenu = QMenu()
        self.trayIcon.setContextMenu(self.trayIconMenu)
        self.trayIcon.contextMenu().addMenu(self.fileMenu)
        self.trayIcon.contextMenu().addMenu(self.toolsMenu)
        self.trayIcon.contextMenu().addMenu(self.helpMenu)
        self.trayIcon.contextMenu().addAction(self.showAction)

        self.rules = []
        self.highlighter = Highlighter(self.logView.document(), self.rules)

        self.pattern = ''  # pattern to be matched
        # explicitly define these since
        # we'll be testing for it later
        self.fileContents = ''
        self.logFile = ''

        self.watch = None

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
            if self.watch:
                self.watch.stop()
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
            try:
                f = open(fname[0], 'r')
            except Exception as e:
                self.statusBar().showMessage('Error: ' + str(e))
                return
            self.logFile = fname[0]
            with f:
                try:
                    self.fileContents = f.read()
                    if not self.watch:
                        self.watch = Watch(self.logFile, self.refreshLogView)
                        self.watch.start()
                    else:
                        self.watch.updatePath(self.logFile)
                    self.statusBar().showMessage('Log file loaded!')
                    self.updateLogView()
                except Exception as e:
                    self.statusBar().showMessage('Error: ' + str(e))
                    self.logFile = ''
        else:
            self.statusBar().showMessage('Please select a log file!')

    def minimizeToTray(self, event):
        if self.isVisible():
            self.hide()
            self.trayIcon.setVisible(True)

    def showWindow(self, event):
        self.show()
        self.trayIcon.setVisible(False)

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
            patternFormat = QTextCharFormat()
            patternFormat.setForeground(Qt.darkRed)
            patternFormat.setFontWeight(QFont.Bold)
            patternReg = QRegularExpression(self.pattern)
            self.rules = [HighlightRule(patternReg, patternFormat)]
            self.highlighter.updateRules(self.rules)
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
            if self.trayIcon.isVisible():
                self.trayIcon.showMessage(
                    "New match!",
                    self.fileContentsList[-1])
            self.statusBar().showMessage(
                "Matched " + str(len(self.fileContentsList)) + " occurences!")
            self.logView.updateContents(
                self.fileContentsList, self.fileLineNumbers)

    def refreshLogView(self, event):
        if not self.logFile:
            return
        try:
            f = open(self.logFile, 'r')
        except Exception as e:
            self.statusBar().showMessage('Error: ' + str(e))
            return
        with f:
            self.fileContents = f.read()
            self.statusBar().showMessage('Refreshed!')
            self.updateLogView()

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
                </a>,
                <a href="https://pypi.python.org/pypi/watchdog">
                    Watchdog
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
