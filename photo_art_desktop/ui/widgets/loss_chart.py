"""
Loss chart widget using PyQtGraph for real-time training visualization
"""
from typing import List, Tuple

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt

import pyqtgraph as pg


class LossChart(QWidget):
    """Real-time loss curve chart widget"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.loss_data: List[Tuple[int, float]] = []

        layout = pg.QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground("w")
        self.plot_widget.setLabel("left", "Loss")
        self.plot_widget.setLabel("bottom", "Step")
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setYRange(0, 0.1)

        # Configure plot line
        self.curve = self.plot_widget.plot(pen=pg.mkPen(color="#3498db", width=2))

        layout.addWidget(self.plot_widget)

    def update_loss(self, step: int, loss: float):
        """Add a new loss data point"""
        self.loss_data.append((step, loss))
        if len(self.loss_data) > 500:
            self.loss_data.pop(0)

        steps = [d[0] for d in self.loss_data]
        losses = [d[1] for d in self.loss_data]

        self.curve.setData(steps, losses)

        # Auto-scale Y axis
        if losses:
            max_loss = max(losses)
            min_loss = min(losses)
            margin = (max_loss - min_loss) * 0.1 if max_loss != min_loss else 0.01
            self.plot_widget.setYRange(min(0, min_loss - margin), max_loss + margin)

    def clear(self):
        """Clear all data"""
        self.loss_data = []
        self.curve.setData([], [])
