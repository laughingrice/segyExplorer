import sys
import argparse

from PyQt5 import QtWidgets

from MainWindow import SegyMainWindow


if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)

	parser = argparse.ArgumentParser()
	parser.add_argument('input', nargs='?', help='file to process')
	args = parser.parse_args()

	window = SegyMainWindow()

	if args.input:
		window.OpenSegy(args.input)

	window.show()

	sys.exit(app.exec_())
