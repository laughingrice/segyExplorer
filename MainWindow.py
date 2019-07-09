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
from PyQt5 import uic
import os

import numpy as np
import segyio


class SegyMainWindow(QtWidgets.QMainWindow):
	def __init__(self, ):
		super().__init__()

		ui_path = os.path.dirname(os.path.abspath(__file__))
		ui_file = os.path.join(ui_path, "MainWindow.ui")


		uic.loadUi(ui_file, self)


	def onOpen(self):
		fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '', 'All Files (*);;DICOM Files (*.dcm)')

		if fileName:
			self.OpenSegy(fileName)


	def onColorRangeChange(self):
		if not 'img' in self.__dict__:
			return

		self.img.set_clim(self.colorRange.start(), self.colorRange.end())
		self.mplWindow.canvas.draw()


	def onColorRangeTextChange(self):
		if not 'img' in self.__dict__:
			return

		try:
			m = int(self.colorRangeTextMin.text())
			M = int(self.colorRangeTextMax.text())

			if m <= M:
				self.colorRange.setRange(m, M)
		except:
			pass # We don't care about exceptions here, mostly letting the user adjust variables until the work for them


	def onDataRangeChange(self):
		if not 'data' in self.__dict__:
			return

		self.img = self.mplWindow.ax.imshow(self.data[self.dataRange.start():self.dataRange.end(), :].T, aspect='auto', cmap='gray')
		self.img.set_clim(self.colorRange.start(), self.colorRange.end())
		self.mplWindow.fig.colorbar(self.img, cax=self.mplWindow.cax)
		self.mplWindow.canvas.draw()


	def onDataRangeTextChange(self):
		if not 'img' in self.__dict__:
			return

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
				self.headerTree.clear()
				self.headerTree.setHeaderLabels(['tag', 'value'])

				for k in s.bin.keys():
					self.headerTree.addTopLevelItem(QtWidgets.QTreeWidgetItem([str(k), str(s.bin[k])]))

				self.traceTree.clear()
				self.traceTree.setHeaderLabels([str(k) for k in s.header[0].keys()])

				for h in s.header:
					self.traceTree.addTopLevelItem(QtWidgets.QTreeWidgetItem([str(v) for v in h.values()]))

				self.data = np.zeros((s.tracecount, s.bin[segyio.BinField.Samples]), s.dtype)

				for i in range(s.tracecount):
					self.data[i, :] = s.trace[i]

				# Set color range before displaying image as a workaround for now as this changes the color scale
				# and the slider bar does not support fractional values so nothing is shown if the range is bellow 1
				self.colorRange.setMin(int(np.floor(np.min(self.data))))
				self.colorRange.setStart(self.colorRange.min())
				self.colorRangeTextMin.setText('{}'.format(self.colorRange.min()))
				self.colorRange.setMax(int(np.ceil(np.max(self.data))))
				self.colorRange.setEnd(self.colorRange.max())
				self.colorRangeTextMax.setText('{}'.format(self.colorRange.max()))
				self.colorRange.update()

				self.dataRange.setMin(0)
				self.dataRange.setStart(self.dataRange.min())
				self.dataRangeTextMin.setText('{}'.format(self.dataRange.min()))
				self.dataRange.setMax(self.data.shape[0])
				self.dataRange.setEnd(self.dataRange.max())
				self.dataRangeTextMax.setText('{}'.format(self.dataRange.max()))
				self.dataRange.update()

				self.img = self.mplWindow.ax.imshow(self.data.T, aspect='auto', cmap='gray')
				self.mplWindow.fig.colorbar(self.img, cax=self.mplWindow.cax)
				self.mplWindow.canvas.draw()


		except OSError as e:
			print('Failed to open file {} - {}'.format(file, e.args[0]))
