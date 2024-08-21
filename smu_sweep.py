import pyvisa
import time
import numpy as np

rm = pyvisa.ResourceManager()
smu = rm.open_resource("USB0::0x0957::0x8E18::MY51143197::0::INSTR")

#SWEEP mode "B2910command.pdf#page=250"
smu.write(':SOUR1:VOLT:MODE SWE')
smu.write(':SOUR1:VOLT:STAR 0.0')
smu.write(':SOUR1:VOLT:STOP 1.0')
smu.write(':SOUR1:SWE:POIN 11')
smu.write(':TRIG1:ALL:COUN 10')
smu.write(':TRIG1:ALL:DEL 0')
smu.write(':TRIG1:ALL:TIM 0.5')
smu.write(':TRIG1:ALL:SOUR TIM')
smu.write(':FORM:ELEM:SENS VOLT,CURR')

smu.write('*CLS')
smu.write('*ESE 1')
smu.write(':INIT (@1)')
smu.write('*OPC')

#測定終了判定
iter = 0
while(True):
    time.sleep(0.5)
    val, _ = rm.visalib.read_stb(smu.session)
    print(f'{iter}: {val:x}')
    if val & 0x20 == 0x20:
        break
    iter = iter + 1

smu.write(":FETC:ARR? (@1)")
ret = smu.read()
ret = ret.split(',')
ret = np.array(ret, dtype=float)
ret = ret.reshape( (len(ret)//2, 2))
xx = ret[:,0]
yy = ret[:,1]

print(xx, yy)

smu.write('outp1 off')

