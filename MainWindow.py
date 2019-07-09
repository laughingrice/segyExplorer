from PyQt5 import QtWidgets
from PyQt5 import uic
import os

import numpy as np
import matplotlib.pyplot as plt
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


	def OpenSegy(self, file):

		with segyio.open(file, strict=False) as s:
			self.headerTree.clear()
			self.headerTree.setHeaderLabels(['tag', 'value'])

			for k in s.bin.keys():
				self.headerTree.addTopLevelItem(QtWidgets.QTreeWidgetItem([str(k), str(s.bin[k])]))

			self.traceTree.clear()
			self.traceTree.setHeaderLabels([str(k) for k in s.header[0].keys()])

			for h in s.header:
				self.traceTree.addTopLevelItem(QtWidgets.QTreeWidgetItem([str(v) for v in h.values()]))

			data = np.zeros((s.tracecount, s.bin[segyio.BinField.Samples]), s.dtype)

			for i in range(s.tracecount):
				data[i, :] = s.trace[i]

			self.mplWindow.ax.imshow(data.T, aspect='auto', cmap='gray')
			self.mplWindow.fig.tight_layout()
			self.mplWindow.canvas.draw()