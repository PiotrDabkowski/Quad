try:
    import RPIO
    import RTIMU
except:
    raise ImportError('You can only run this module on raspberry pi connected to Quad :)')

from threading import Thread
import time



from motor import Motors
from communication.link import Link
from communication.handlers.commander import InCommander
from communication.handlers.info import OutInfo
from communication.handlers.status import OutStatus
from communication.in_handle import InPost
from communication.out_handle import OutPost


SETTINGS_FILE = "RTIMULib"
def computeHeight(pressure):
    return 44330.8 * (1 - pow(pressure / 1013.25, 0.190263));


class Quad:
    """Contains whole state of the quad and allows control of the quad through high level functions
       Supports communication with master PC.
       You have to call start function to start everything.
       Commands like:
           hover(pos=None)  -> keeps current position or goes to required pos if pos set.

        Quad lands/returns home if does not receive command from PC for some time."""

    def __init__(self):
        # initialise motors
        self.motors = Motors()

        # initialise communication
        self._link = Link(quad=True)  # communication link through my website hehe, quite slow but works for now
        # IN handlers
        self.in_handlers = [InCommander(self)]
        # OUT handlers - they will be accessed directly so they need to have separate names
        self.messenger = OutInfo()
        self.updater = OutStatus(self, send_stamp=True)
        self.out_handlers = [self.messenger, self.updater]
        # Initialise posts, they will not be called directly.
        self.in_post = InPost(self._link, handlers=self.in_handlers)
        self.out_post = OutPost(self._link, handlers=self.out_handlers)

        # initialise state:
        # following are always best estimates:
        self.pos = [0,0,0]
        self.geo_pos = [0,0,0] # position in GPS format
        self.vel = [0,0,0]
        self.angle = [0,0,0]
        self.avel = [0,0,0]
        self.cells = [3.9,3.9,3.9,3.9]
        self._status = {}


    def start(self):
        """Infinite loop, starts all necessary threads and runs infinite update_state loop.
           You have to call this function before using quad - does not return"""
        out = Thread(target=self.in_post._handle_loop)  # executes commands from master
        inp = Thread(target=self.out_post._handle_loop)  # sends important parameters to the master
        out.daemon = inp.daemon = True
        out.start()
        inp.start()
        self._update_state()  # gets data from sensors, this will be main thread.

    def _get_status(self):
        s = {}
        s['fusionPose'] = self._status['fusionPose']
        return s

    def _update_state(self):
        s = RTIMU.Settings(SETTINGS_FILE)
        imu = RTIMU.RTIMU(s)
        pressure = RTIMU.RTPressure(s)

        if (not imu.IMUInit()):
            self.messenger.send("IMU Init Failed")
            raise RuntimeError('IMU failed! Cant fly')
        else:
            self.messenger.send("IMU Init Succeeded. Soon you will receive status updates...")
        imu.setSlerpPower(0.02)
        imu.setGyroEnable(True)
        imu.setAccelEnable(True)
        imu.setCompassEnable(True)
        poll_interval = imu.IMUGetPollInterval()
        self.messenger.send('Started polling IMU...')
        n = 0
        sep = int(100/poll_interval)
        print 'sep', sep
        while True:
            if imu.IMURead():
                #x, y, z = imu.getFusionData()
                # print("%f %f %f" % (x,y,z))
                data = imu.getIMUData()
                (data["pressureValid"], data["pressure"], data["temperatureValid"],
                 data["temperature"]) = pressure.pressureRead()
                self._status = data
                if not n%sep:
                    self.updater.send_status()
                time.sleep(poll_interval * 1.0 / 1000.0)
                n += 1

    def _update_motors(self):
        pass





if __name__=='__main__':
    q = Quad()
    print 'Init ok'
    try:
        q.start()
    finally:
        q.updater.send_status()
        q.messenger.send('ended')
        time.sleep(5) # wait for all messages to be sent
    # shutdown :(