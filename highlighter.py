# adapted from:
# http://doc.qt.io/qt-5/qtwidgets-richtext-syntaxhighlighter-example.html
from PyQt5.QtGui import QSyntaxHighlighter


class HighlightRule(object):

    def __init__(self, pattern, format_):
        self.pattern = pattern
        self.format = format_


class Highlighter(QSyntaxHighlighter):

    """
    A nifty highlighter for making sure you see what you matched
    """

    def __init__(self, parentDocument, rules):
        """
        Initialize!!!! parentDocument a QTextDocument instance
        """
        super().__init__(parentDocument)
        self.rules = rules

    def highlightBlock(self, text):
        """
        Paint em like you mean it!!!
        """
        for rule in self.rules:
            matchIterator = rule.pattern.globalMatch(text)
            while matchIterator.hasNext():
                match = matchIterator.next()
                self.setFormat(
                    match.capturedStart(),
                    match.capturedEnd(),
                    rule.format)

    def updateRules(self, rules):
        self.rules = rules
