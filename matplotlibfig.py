# segyExplorer - display segy file data and header information
# Copyright (C) 2019 Micha Feigin-Almon
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
		self.ax, self.cax = self.canvas.figure.subplots(1,2, gridspec_kw={'width_ratios': [20, 1], 'wspace': 0.03, 'left': 0.04, 'right': 0.95, 'top': 0.99, 'bottom': 0.04})

		# Add a layout to the widget
		self.vbl = QtWidgets.QVBoxLayout()
		self.vbl.addWidget(self.toolbar)
		self.vbl.addWidget(self.canvas)
		self.setLayout(self.vbl)
