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
