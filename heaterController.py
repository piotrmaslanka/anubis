"""
A controller that
1) accepts TP telegrams and sets physicalModel appropriately
2) accepts ST telegrams and cancels everything
"""

from threading import Thread
from time import sleep
from collections import deque

class Controller(Thread):
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
            print "Entering new mode, TEMP=%s, TIME=%s seconds" % (self.currentSetpoint, self.timeRemaining)
            self.model.setpoint = self.currentSetpoint
            self.programNo += 1
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
                    # Nothing! Reset the heater
                    self.model.unset()
                    self.programNo = 0
                    self.status = 0
            else:
                if abs(self.model.temperature - self.model.setpoint) > 2:
                    self.status = 1
                else:
                    if self.status == 1:
                        print "Temperature reached, holding"
                    self.status = 2
                        
                    self.timeRemaining -= 1