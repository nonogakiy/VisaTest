import sys
import numpy as np
from PySide6.QtWidgets import *
from PySide6.QtCore import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import pyvisa
import time

class WinTest(QWidget):
    #GUI init
    def __init__(self):
        super().__init__()
        self.setWindowTitle('matplotlibTest')
        #Layout
        hbox = QHBoxLayout()
        vbox = QVBoxLayout()
        #
        plotfig = plt.figure(figsize=(5,3))
        self.axis = plotfig.add_subplot(1,1,1)
        self.canvas = FigureCanvas(plotfig)
        #       
        self.btnMeas = QPushButton('Measure', self)
        self.btnMeas.clicked.connect(self.onBtnMeasClicked)
        #
        vbox.addWidget(self.btnMeas)
        vbox.addStretch()
        #
        hbox.addWidget(self.canvas)
        hbox.addLayout(vbox)
        #
        self.setLayout(hbox)

        self.rm = pyvisa.ResourceManager()
        self.smu = self.rm.open_resource("USB0::0x0957::0x8E18::MY51143197::0::INSTR")
        #
    #Event
    def onBtnMeasClicked(self):
        xx = np.linspace(0, 10, 100)
        yy = np.sin(xx)
        self.axis.plot(xx, yy, '-')
        self.canvas.draw()
        print('push First')
    #

qApp = QApplication(sys.argv)
app_main = WinTest()
app_main.show()

qApp.exec()