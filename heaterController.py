"""
A controller that
1) accepts TP telegrams and sets physicalModel appropriately
2) accepts ST telegrams and cancels everything
"""

from threading import Thread

class Controller(Thread):
    def __init__(self, physicalModel):
        self.model = physicalModel