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
        self.max_steps: int = 500

        layout = pg.QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground("w")
        self.plot_widget.setLabel("left", "Loss")
        self.plot_widget.setLabel("bottom", "Step")
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setYRange(0.01, 0.1)
        self.plot_widget.setXRange(0, self.max_steps)

        # Configure plot line
        self.curve = self.plot_widget.plot(pen=pg.mkPen(color="#3498db", width=2))

        layout.addWidget(self.plot_widget)

    def set_max_steps(self, steps: int):
        """Set the maximum steps for X-axis range"""
        if steps > 0:
            self.max_steps = steps
            self.plot_widget.setXRange(0, steps)

    def update_loss(self, step: int, loss: float):
        """Add a new loss data point"""
        if loss <= 0:
            return

        self.loss_data.append((step, loss))
        if len(self.loss_data) > 500:
            self.loss_data.pop(0)

        steps = [d[0] for d in self.loss_data]
        losses = [d[1] for d in self.loss_data]

        self.curve.setData(steps, losses)

        # Auto-scale Y axis based on actual loss values
        if losses:
            min_loss = min(losses)
            max_loss = max(losses)
            if max_loss - min_loss < 0.001:
                y_min = min_loss * 0.9 if min_loss > 0 else 0
                y_max = min_loss * 1.1 if min_loss > 0 else 0.1
            else:
                margin = (max_loss - min_loss) * 0.15
                y_min = min_loss - margin
                y_max = max_loss + margin
            self.plot_widget.setYRange(max(0, y_min), y_max)

    def clear(self):
        """Clear all data"""
        self.loss_data = []
        self.curve.setData([], [])
