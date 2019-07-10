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
		self._data = None


	def onOpen(self):
		fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '', 'All Files (*);;segy Files (*.segy)')

		if fileName:
			self.OpenSegy(fileName)


	def onColorRangeChange(self):
		if self._img is None:
			return

		linked = self.colorRangeLinked.isChecked()
		self.colorRangeMin.setEnabled(False if linked else True)

		c = self.colorRangeMin.value()
		C = self.colorRangeMax.value()

		if linked:
			c = self.colorRangeMin.minimum() + (self.colorRangeMax.maximum() - C)
			self.colorRangeMin.setValue(c)

		if self.c == c and self.C == C:
			return

		self.c = c
		self.C = C

		self._img.set_clim(self.c, self.C)
		self.mplWindow.canvas.draw()


	def onDataRangeChange(self):
		if self._data is None:
			return

		m = self.dataRangeMin.value()
		M = self.dataRangeMax.value()

		if m == self.m and M == self.M:
			return

		if m > M:
			t = m
			m = M
			M = t

		self.m = m
		self.M = M

		self.mplWindow.ax.clear()
		self.mplWindow.cax.clear()

		self._img = self.mplWindow.ax.imshow(self._data[self.m:self.M+1, :].T, aspect='auto', cmap='gray', vmin=self.c, vmax=self.C, extent=[self.m, self.M, 0, self._data.shape[1]])
		self.mplWindow.fig.colorbar(self._img, cax=self.mplWindow.cax)

		self.mplWindow.canvas.draw()


	def onDataJumpRight(self):
		m = self.dataRangeMin.value()
		M = self.dataRangeMax.value()

		if M == self.dataRangeMax.maximum():
			return

		step = (M - m + 1) * self.dataJumpStep.value()
		M = min(M + step, self.dataRangeMax.maximum())
		m = M - step + 1

		self.dataRangeMin.setValue(m)
		self.dataRangeMax.setValue(M)

		self.onDataRangeChange()

	def onDataJumpLeft(self):
		m = self.dataRangeMin.value()
		M = self.dataRangeMax.value()

		if m == self.dataRangeMax.minimum():
			return

		step = M - m + 1
		m = max(m - step, self.dataRangeMin.minimum())
		M = m + step - 1

		self.dataRangeMin.setValue(m)
		self.dataRangeMax.setValue(M)

		self.onDataRangeChange()


	def OpenSegy(self, file: str):
		try:
			with segyio.open(file, strict=False) as s:
				self._img = None
				self._data = None

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
				self.c = np.min(data)
				self.C = np.max(data)

				self.colorRangeLinked.setChecked(True if self.c < 0 else False)
				self.colorRangeMin.setEnabled(False if self.colorRangeLinked.isChecked() else True)

				self.colorRangeMin.setMinimum(self.c)
				self.colorRangeMin.setMaximum(0.5 * (self.c + self.C) if self.colorRangeLinked.isChecked() else self.C)
				self.colorRangeMin.setSingleStep((self.C - self.c) / 40)
				self.colorRangeMax.setMinimum(0.5 * (self.c + self.C) if self.colorRangeLinked.isChecked() else self.c)
				self.colorRangeMax.setMaximum(self.C)
				self.colorRangeMax.setSingleStep((self.C - self.c) / 40)

				self.colorRangeMin.setValue(self.c)
				self.colorRangeMax.setValue(self.C)

				self.m = 0
				self.M = data.shape[0]-1

				self.dataRangeMin.setMinimum(0)
				self.dataRangeMin.setMaximum(self.M)
				self.dataRangeMin.setValue(self.m)
				self.dataRangeMax.setMinimum(0)
				self.dataRangeMax.setMaximum(self.M)
				self.dataRangeMax.setValue(self.M)

				self._data = data

				self.mplWindow.ax.clear()
				self.mplWindow.cax.clear()

				self._img = self.mplWindow.ax.imshow(self._data.T, aspect='auto', cmap='gray')
				self.mplWindow.fig.colorbar(self._img, cax=self.mplWindow.cax)

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