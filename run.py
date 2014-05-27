# coding=UTF-8
print "Made-Up Devices Production Company Proudly Presents:"
print "Anubis - a Virtual Heater for Heating Radiometers"
print "(because you can't afford a real one)"

print "Select COM port (enter stuff like COM1): "
#from serial import Serial
import time
#serial = Serial(raw_input(), baudrate=2400, parity='N', stopbits=1, dsrdtr=True)
from physicalModel import HeaterPhysicalModel
from heaterController import Controller

hpm = HeaterPhysicalModel()
cntrl = Controller(hpm)

hpm.start()
cntrl.start()

while True:
    #telecom = serial.readline()
    pass
    
    #print "Received telegram "+telecom.strip()



# Possible telegrams:
#   TP <3 digits of temperature> <two digits of hours> <two digits of minutes> <two digits of seconds>
#               add a setpoint and a time
#   NA - cancel everything
#   ST - inquiry for temperature and status
# command is terminated by \n
