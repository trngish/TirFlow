"""
Log viewer widget for displaying training and preprocessing logs
"""
from PySide6.QtWidgets import QTextEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCursor


class LogViewer(QTextEdit):
    """Read-only log display widget"""

    def __init__(self, parent=None, max_lines: int = 500):
        super().__init__(parent)

        self.max_lines = max_lines
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 9))
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
            }
        """)

    def append_log(self, text: str):
        """Append a line of log text"""
        self.append(text)
        self._trim_lines()

    def set_log(self, text: str):
        """Set the entire log content"""
        self.setPlainText(text)
        self._trim_lines()
        self.moveCursor(QTextCursor.MoveOperation.End)

    def _trim_lines(self):
        """Trim log to max lines"""
        doc = self.document()
        if doc.blockCount() > self.max_lines:
            cursor = QTextCursor(doc)
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            for _ in range(doc.blockCount() - self.max_lines):
                cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
                cursor.removeSelectedText()
                cursor.deleteChar()
