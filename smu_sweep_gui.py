import sys
import numpy as np
import pyvisa
import time
from PySide6.QtWidgets import *
from PySide6.QtCore import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas


class WinTest(QWidget):
    #GUI init
    def __init__(self):
        super().__init__()
        self.setWindowTitle('matplotlibTest')
        # Elemental Layouts
        hbox = QHBoxLayout()
        vbox = QVBoxLayout()
        # Including MatPlotLIb
        plotfig = plt.figure(figsize=(5,3))
        self.axis = plotfig.add_subplot(1,1,1)
        self.canvas = FigureCanvas(plotfig)
        # MeasureButton
        self.btnMeas = QPushButton('Measure')
        self.btnMeas.clicked.connect(self.onBtnMeasClicked)
        # StatusLabel
        self.lblStatus = QLabel('Status:')
        # VBox Construction
        vbox.addWidget(self.btnMeas)
        vbox.addStretch()
        vbox.addWidget(self.lblStatus)
        # HBox Construction
        hbox.addWidget(self.canvas)
        hbox.addLayout(vbox)
        # Layout Construction
        self.setLayout(hbox)
        # Init VISA Resource
        self.rm = pyvisa.ResourceManager()
        self.smu = self.rm.open_resource("USB0::0x0957::0x8E18::MY51143197::0::INSTR")
        # RunRoop Timer Setting
        self.timer = QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.onTimerTick)
        # Measurement valiables
        self.measuring = False
        self.iter = 0
    # Timer Event
    def onTimerTick(self):
        if self.measuring == True:
            # Query Standard Event Status
            val, _ = self.rm.visalib.read_stb(self.smu.session)
            self.lblStatus.setText(f'Status: {self.iter}-{val:x}')
            # MeasureEnd Detection
            if val & 0x20 == 0x20:
                self.measuring = False
                self.timer.stop()
                # Fetch Data
                self.smu.write(":FETC:ARR? (@1)")
                ret = self.smu.read()
                # Plot Data
                ret = ret.split(',')
                ret = np.array(ret, dtype=float)
                ret = ret.reshape( (len(ret)//2, 2))
                xx = ret[:,0]
                yy = ret[:,1]
                self.smu.write('outp1 off')
                self.axis.plot(xx, yy, '-o')
                self.canvas.draw()
                # Preparation for re-measurement
                self.btnMeas.setText('Measure')
            else:
                self.iter += 1
        else:
            # Not measuring But timer alive
            self.measuring = False
            self.timer.stop()
    # Measure Start Event
    def onBtnMeasClicked(self):
        if self.btnMeas.text() == 'Measure':
            # MeasureButton Pushed
            # Measurement Conditions
            self.smu.write(':SOUR1:VOLT:MODE SWE')
            self.smu.write(':SOUR1:VOLT:STAR 0.0')
            self.smu.write(':SOUR1:VOLT:STOP 1.0')
            self.smu.write(':SOUR1:SWE:POIN 11')
            self.smu.write(':TRIG1:ALL:COUN 11')
            self.smu.write(':TRIG1:ALL:DEL 0')
            self.smu.write(':TRIG1:ALL:TIM 0.5')
            self.smu.write(':TRIG1:ALL:SOUR TIM')
            self.smu.write(':FORM:ELEM:SENS VOLT,CURR')
            # start commands
            self.smu.write('*CLS')
            self.smu.write('*ESE 1')
            self.smu.write(':INIT (@1)')
            self.smu.write('*OPC')
            # timmer starts
            self.measuring = True
            self.iter = 0
            self.timer.start()
            time.sleep(0.5)
            # Preparation for Abort
            self.btnMeas.setText('Abort!')
        else:
            # AbortButton Pushed
            self.smu.write(':ABOR:ALL')
            self.smu.write(':OUTP1 OFF')
            self.measuring = False
            self.iter = 0
            self.btnMeas.setText('Measure')
#
qApp = QApplication(sys.argv)
app_main = WinTest()
app_main.show()

qApp.exec()