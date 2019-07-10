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

from PyQt5 import QtWidgets, QtCore
from PyQt5 import uic
import os

import numpy as np
import pandas as pd
import segyio


class SegyMainWindow(QtWidgets.QMainWindow):
	def __init__(self, ):
		super().__init__()

		ui_path = os.path.dirname(os.path.abspath(__file__))
		ui_file = os.path.join(ui_path, "MainWindow.ui")
		uic.loadUi(ui_file, self)

		self.img = None
		self.data = None


	def onOpen(self):
		fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '', 'All Files (*);;segy Files (*.segy)')

		if fileName:
			self.OpenSegy(fileName)


	def onColorRangeChange(self):
		if self.img is None:
			return

		if self.c == self.colorRange.start() and self.C == self.colorRange.end():
			return

		self.c = self.colorRange.start()
		self.C = self.colorRange.end()

		self.img.set_clim(self.c, self.C)
		self.mplWindow.canvas.draw()


	def onColorRangeTextChange(self):
		try:
			c = int(self.colorRangeTextMin.text())
			C = int(self.colorRangeTextMax.text())

			if c <= C:
				self.colorRange.setRange(c, C)
		except:
			pass # We don't care about exceptions here, mostly letting the user adjust variables until the work for them


	def onDataRangeChange(self):
		if self.data is None:
			return

		if self.m == self.dataRange.start() and self.M == self.dataRange.end():
			return

		self.m = self.dataRange.start()
		self.M = self.dataRange.end()

		self.img = self.mplWindow.ax.imshow(self.data[self.m:self.M+1, :].T, aspect='auto', cmap='gray', vmin=self.c, vmax=self.C, extent=[self.m, self.M, 0, self.data.shape[1]])
		self.mplWindow.fig.colorbar(self.img, cax=self.mplWindow.cax)
		self.mplWindow.canvas.draw()


	def onDataRangeTextChange(self):
		try:
			m = int(self.dataRangeTextMin.text())
			M = int(self.dataRangeTextMax.text())

			if m <= M:
				self.dataRange.setRange(m, M)
		except:
			pass # We don't care about exceptions here, mostly letting the user adjust variables until the work for them


	def OpenSegy(self, file: str):
		try:
			with segyio.open(file, strict=False) as s:
				self.img = None
				self.data = None

				s.mmap()

				self.fileHeader = pd.DataFrame(columns=['tag','values'], index=range(len(s.bin)), dtype=str)
				for i, val in enumerate(s.bin.items()):
					self.fileHeader.iloc[i,:] = [str(v) for v in val]
				self.fileHeaderTable.setModel(PandasModel(self.fileHeader))

				traceHeaderData = np.empty((len(s.header), len(s.header[0].keys())), dtype=np.int32)
				for i, val in enumerate(s.header):
					traceHeaderData[i, :] = [x for x in val.values()]
				self.traceHeader = pd.DataFrame(data=traceHeaderData, columns=[str(k) for k in s.header[0].keys()])
				self.traceHeaderTable.setModel(PandasModel(self.traceHeader))

				data = np.zeros((s.tracecount, s.bin[segyio.BinField.Samples]), s.dtype)
				for i in range(s.tracecount):
					data[i, :] = s.trace[i]

				# Set color range before displaying image as a workaround for now as this changes the color scale
				# and the slider bar does not support fractional values so nothing is shown if the range is bellow 1
				self.c = int(np.floor(np.min(data)))
				self.C = int(np.ceil(np.max(data)))
				self.colorRange.setMin(self.c)
				self.colorRange.setStart(self.c)
				self.colorRangeTextMin.setText('{}'.format(self.c))
				self.colorRange.setMax(self.C)
				self.colorRange.setEnd(self.C)
				self.colorRangeTextMax.setText('{}'.format(self.C))
				self.colorRange.update()

				self.m = 0
				self.M = data.shape[0]-1
				self.dataRange.setMin(self.m)
				self.dataRange.setStart(self.m)
				self.dataRangeTextMin.setText('{}'.format(self.m))
				self.dataRange.setMax(self.M)
				self.dataRange.setEnd(self.M)
				self.dataRangeTextMax.setText('{}'.format(self.M))
				self.dataRange.update()

				self.data = data
				self.img = self.mplWindow.ax.imshow(self.data.T, aspect='auto', cmap='gray')

				self.mplWindow.fig.colorbar(self.img, cax=self.mplWindow.cax)
				self.mplWindow.canvas.draw()
		except Exception as e:
			print('Failed to open file {} - {}'.format(file, e.args[0]))


class PandasModel(QtCore.QAbstractTableModel):
	def __init__(self, data, parent=None):
		super(PandasModel, self).__init__()
		self._data = data


	def rowCount(self, parent=None):
		return self._data.shape[0]


	def columnCount(self, parent=None):
		return self._data.shape[1]


	def headerData(self, idx, orientation, role):
		if role != QtCore.Qt.DisplayRole:
			return None

		if orientation == QtCore.Qt.Horizontal:
			return self._data.columns[idx]
		if orientation == QtCore.Qt.Vertical:
			return self._data.index[idx]

		return None


	def data(self, index, role=QtCore.Qt.DisplayRole):
		if not index.isValid():
			return None

		if role == QtCore.Qt.DisplayRole:
			return str(self._data.values[index.row(),index.column()])

		return None


	def flags(self, index):
		flags = super(self.__class__, self).flags(index)
		flags |= QtCore.Qt.ItemIsSelectable
		flags |= QtCore.Qt.ItemIsEnabled

		return flags


	def sort(self, Ncol, order):
		try:
			self.layoutAboutToBeChanged.emit()
			self._data = self._data.sort_values(self._data.columns[Ncol], ascending=not order)
			self.layoutChanged.emit()
		except Exception as e:
			print(e)