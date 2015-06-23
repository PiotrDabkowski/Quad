from motor import Motors
from communication import Link
from threading import Thread

class Quad:
    """Contains whole state of the quad and allows control of the quad through high level functions
       Supports communication with master PC.
       You have to call start function to start everything.
       Commands like:
           hover(pos=None)  -> keeps current position or goes to required pos if pos set.

        Quad lands/returns home if does not receive command from PC for some time."""

    def __init__(self):
        self.motors = Motors()
        self.link = Link()


    def start(self):
         ex = Thread(target=self._execute_commands)  # executes commands from master
         com = Thread(target=self._communicate)  # sends important parameters to the master
         mot = Thread(target=self._update_motors)  # updates motors accordingly
         ex.daemon = com.daemon = mot.daemon = True
         ex.start()
         com.start()
         mot.start()
         self._update_state()  # gets data from sensors, this will be main thread.


    def _execute_commands(self):
        pass

    def _communicate(self):
        pass

    def _update_state(self):
        pass

    def _update_motors(self):
        pass


