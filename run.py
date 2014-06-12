# coding=UTF-8
print "Anubis - a heater simulator (because you can't afford a real one)"
print "visit http://github.com/piotrmaslanka/anubis for source and license"
print "Select COM port (enter stuff like COM1): "

from serial import Serial
import time
from time import sleep
from threading import Thread
from collections import deque

serial = Serial(raw_input(), baudrate=2400, parity='N', stopbits=1, dsrdtr=True)

class HeaterPhysicalModel(Thread):
    """
    Physical model of a heater.
    
    It lives as a thread - it's just so separate :)
    """
    HEATING_FACTOR = 0.010
    COOLING_FACTOR = 0.005
    
    OVERSHOOT = 50  # for faster heating
    
    AMBIENT_TEMP = 20
    
    def __init__(self):
        Thread.__init__(self)
        self.temperature = self.AMBIENT_TEMP        #: volatile public
        self.setpoint = self.AMBIENT_TEMP           #: volatile public, change to set setpoint

    
    def unset(self):
        """Remove any setpoints"""
        self.setpoint = self.AMBIENT_TEMP
    
    def run(self):
        while True:
            sleep(1)
            self.iterate()
        
    def iterate(self):
        """
        Means a discrete amount of time has expired.
        Update own temperature.
        """
        # Environmental cooling
        self.temperature -= (self.temperature - self.AMBIENT_TEMP) * self.COOLING_FACTOR
        
        # Heating
        if self.temperature < self.setpoint:
            self.temperature += (self.setpoint + self.OVERSHOOT - self.temperature) * self.HEATING_FACTOR
        
class Controller(Thread):
    """
    A controller that
    1) accepts TP telegrams and sets physicalModel appropriately
    2) accepts ST telegrams and cancels everything
    """
    def __init__(self, physicalModel):
        Thread.__init__(self)

        self.model = physicalModel
        
        # Current settings
        self.currentSetpoint = None
        self.timeRemaining = 0
        
        # Things to carry out more
        self.orders = deque()
        
        self.programNo = -1      # number of program that is being realized
        self.status = 0
        
        
    def scheduleProgram(self):
        """Try to schedule a new program - if it's possible
        @return bool: whether anything was scheduled at all"""
        
        should_schedule = (len(self.orders) > 0) and (self.timeRemaining == 0)
        
        if should_schedule:
            # ok, a new order!
            self.currentSetpoint, self.timeRemaining = self.orders.pop()
            self.programNo += 1
            print "Entering program %d, %sC for %s seconds" % (self.programNo, self.currentSetpoint, self.timeRemaining)
            self.model.setpoint = self.currentSetpoint
            self.wasTempReached = False     
            self.status = 1
            return True
        return False
        
    def onTP(self, temperature, hours, minutes, seconds):
        """A TP telegram arrived"""
        print "ST telegram received, heat %sC for %s:%s:%s" % (temperature, hours, minutes, seconds)
        self.orders.appendleft((temperature, hours * 3600 + minutes * 60 + seconds))
        self.scheduleProgram()
        
    def onNA(self):
        """A NA telegram arrived"""
        print "NA telegram received; aborting heating"
        self.orders = deque()
        self.currentSetpoint = None
        self.timeRemaining = 0
        self.model.unset()
        self.programNo = -1
        self.status = 0 # status for ST command
                        # 0 - standby
                        # 1 - temperature unstable
                        # 2 - temperature stable, holding
        
    def run(self):
        while True:
            sleep(1)
            
            # What should I do?
            if self.timeRemaining == 0:
                if not self.scheduleProgram():
                    if self.status != 0:
                        print "Heating cycle finished. Have a nice day"
                    # Nothing! Reset the heater
                    self.model.unset()
                    self.programNo = 0
                    self.status = 0
            else:
                if (self.model.temperature+2) < self.model.setpoint:
                    self.status = 1
                else:
                    if self.status == 1:
                        print "Temperature reached, holding for %s seconds now" % (self.timeRemaining, )
                    self.status = 2
                        
                    self.timeRemaining -= 1
                    if self.timeRemaining == 0:
                        print "Program %s finished" % (self.programNo, )

hpm = HeaterPhysicalModel()
cntrl = Controller(hpm)

hpm.start()
cntrl.start()

while True:
    telecom = serial.readline()
    try:
        if telecom.startswith('TP'):
            temp = int(telecom[2:5])
            hrs = int(telecom[5:7])
            mins = int(telecom[7:9])
            secs = int(telecom[9:11])
            cntrl.onTP(temp, hrs, mins, secs)
        elif telecom.startswith('NA'):
            cntrl.onNA()
        elif telecom.startswith('ST'):
            serial.write('ST%d%02d%03d\n' % (cntrl.status, cntrl.programNo, int(hpm.temperature), ))
        else:
            raise Exception()
    except Exception as e:
        print "Error: Telegram was %s, reason was %s" % (telecom, e)

# Possible telegrams:
#   TP <3 digits of temperature> <two digits of hours> <two digits of minutes> <two digits of seconds>
#               add a setpoint and a time
#   NA - cancel everything
#   ST - inquiry for temperature and status, respond with:
#           ST<status digit><two digits - current program><three digits - current temperature> 
# command and responses terminated by \n
