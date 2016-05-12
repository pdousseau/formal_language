# coding=utf-8
import sys
sys.path.append("/usr/lib/python2.6/dist-packages/PyQt4")

from Gui.MainWindow import MainWindow
from PyQt4.QtGui import QApplication


app = QApplication(sys.argv)
janela = MainWindow()
janela.show()
app.exec_()
