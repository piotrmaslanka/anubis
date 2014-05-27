from threading import Thread
from time import sleep


class HeaterPhysicalModel(Thread):
    """
    Physical model of a heater.
    
    It lives as a thread - it's just so separate :)
    """
    HEATING_FACTOR = 0.010
    COOLING_FACTOR = 0.005
    
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
            print "TEMP=%.2s SETPOINT=%.2s" % (self.temperature, self.setpoint)
        
    def iterate(self):
        """
        Means a discrete amount of time has expired.
        Update own temperature.
        
        Equations here are discrete version of Newton's heating law
        """
        # Proof
        if self.setpoint < self.AMBIENT_TEMP: self.setpoint = self.AMBIENT_TEMP
        
        # Environmental cooling
        self.temperature -= (self.temperature - self.AMBIENT_TEMP) * self.COOLING_FACTOR
        
        # Heating
        if self.temperature < self.setpoint:
            self.temperature += (self.setpoint - self.temperature) * self.HEATING_FACTOR
        