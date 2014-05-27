# coding=UTF-8
print "Made-Up Devices Production Company Proudly Presents:"
print "Anubis - a Virtual Heater for Heating Radiometers"
print "(because you can't afford a real one)"

print "Select COM port (enter stuff like COM1): "
from serial import Serial
import time
serial = Serial(raw_input(), baudrate=2400, parity='N', stopbits=1, dsrdtr=True)
from physicalModel import HeaterPhysicalModel
from heaterController import Controller

hpm = HeaterPhysicalModel()
cntrl = Controller(hpm)

hpm.start()
cntrl.start()

while True:
    telecom = serial.readline()
    if telecom.startswith(b'TP'):
        temp = int(telecom[2:5])
        hrs = int(telecom[5:7])
        mins = int(telecom[7:9])
        secs = int(telecom[9:11])
        cntrl.onTP(temp, hrs, mins, secs)
    elif telecom.startswith(b'NA'):
        cntrl.onNA()
    elif telecom.startswith(b'ST'):
        serial.write('ST%d%02d%03d\n' % (cntrl.status, cntrl.programNo, int(hpm.temperature), ))
    
    print "Received telegram "+telecom.strip()

# Possible telegrams:
#   TP <3 digits of temperature> <two digits of hours> <two digits of minutes> <two digits of seconds>
#               add a setpoint and a time
#   NA - cancel everything
#   ST - inquiry for temperature and status, respond with:
#           ST<status digit><two digits - current program><three digits - current temperature> 
# command and responses terminated by \n
