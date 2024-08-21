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
        self.lblStatus = QLabel('Status:')
        vbox.addWidget(self.btnMeas)
        vbox.addStretch()
        vbox.addWidget(self.lblStatus)
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
        self.smu.write(':SOUR1:VOLT:MODE SWE')
        self.smu.write(':SOUR1:VOLT:STAR 0.0')
        self.smu.write(':SOUR1:VOLT:STOP 1.0')
        self.smu.write(':SOUR1:SWE:POIN 11')
        self.smu.write(':TRIG1:ALL:COUN 11')
        self.smu.write(':TRIG1:ALL:DEL 0')
        self.smu.write(':TRIG1:ALL:TIM 0.5')
        self.smu.write(':TRIG1:ALL:SOUR TIM')
        self.smu.write(':FORM:ELEM:SENS VOLT,CURR')

        self.smu.write('*CLS')
        self.smu.write('*ESE 1')
        self.smu.write(':INIT (@1)')
        self.smu.write('*OPC')

        #測定終了判定
        iter = 0
        while(True):
            time.sleep(0.5)
            val, _ = self.rm.visalib.read_stb(self.smu.session)
            print(f'{iter}: {val:x}')
            #self.lblStatus.text = f'Status: {iter} -- {val:x}'

            if val & 0x20 == 0x20:
                break
            iter += 1

        self.smu.write(":FETC:ARR? (@1)")
        ret = self.smu.read()
        ret = ret.split(',')
        ret = np.array(ret, dtype=float)
        ret = ret.reshape( (len(ret)//2, 2))
        xx = ret[:,0]
        yy = ret[:,1]
        self.smu.write('outp1 off')
        self.axis.plot(xx, yy, '-o')
        self.canvas.draw()
#
qApp = QApplication(sys.argv)
app_main = WinTest()
app_main.show()

qApp.exec()