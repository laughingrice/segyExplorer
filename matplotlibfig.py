from PyQt5 import QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class matplotlibFig(QtWidgets.QWidget):
	def __init__(self, parent=None):
		super(matplotlibFig, self).__init__(parent)

		# Create the figure and corresponding figure canvas
		self.fig = Figure()
		self.canvas = FigureCanvas(self.fig)
		self.toolbar = NavigationToolbar(self.canvas, self)

		# Add axes
		self.ax = self.canvas.figure.subplots()

		# Add a layout to the widget
		self.vbl = QtWidgets.QVBoxLayout()
		self.vbl.addWidget(self.toolbar)
		self.vbl.addWidget(self.canvas)
		self.setLayout(self.vbl)
