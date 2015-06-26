from threading import Thread
import time, random, math

from communication.link import Link
from communication.handlers.commander import OutCommander
from communication.handlers.info import InInfo
from communication.handlers.status import InStatus
from communication.in_handle import InPost
from communication.out_handle import OutPost

import random
import time
import visual
from PIL import Image
color = visual.color
GROUND_SIZE = 100.0
LEVEL = -0.2
scene = visual.scene
scene.range=3
sep = 1
for e in xrange(-int(GROUND_SIZE/sep/2),int(GROUND_SIZE/sep/2)+1):
    e = e*sep
    co = (1,1,1) #color.green
    visual.curve(pos=[(-GROUND_SIZE/2, e, LEVEL), (GROUND_SIZE/2, e, LEVEL)], color=co)
    visual.curve(pos=[(e,-GROUND_SIZE/2, LEVEL), (e,GROUND_SIZE/2, LEVEL)],color=co)

scene.background = (0.4,0.6,1)
def to_vec(vec):
    if not isinstance(vec, visual.vector):
        return visual.vector(*vec)
    return vec

#GROUND = visual.box(pos=(0,0,-0.01), length=GROUND_SIZE, height=GROUND_SIZE, width=0.02, material=tgrid)


class Quad:
    def __init__(self, diameter=0.65, mass=3.000, motor=None, inertia=None,
                 centre_of_mass_shift=0, pos=visual.vector(0,0,5)):
        """ALL UNITS SHOULD BE SI UNITS (except of propeller diameter which shoud be in INCHES)
           USE KGs, Meters (dont use grams or mm)
            diameter is the distance between diagonal motors
            mass is the total mass of the quadcopter
            inertia is the inertia of the whole quad about its centre of mass if None I will try to estimate the value
                    (I will assume a disc of uniform mass)
            centre_of_mass_shift - the distance between plane containing motors and the centre of mass (positive means ABOVE motors)
        """
        if inertia is None: # assume a disc of uniform density
            inertia = (diameter/2.0)**2*mass/2
        self.inertiaZ = float(inertia)
        self.inertiaX = self.inertiaZ/2
        self.prop_diameter = 15*0.0254
        self.prop_inertia = (self.prop_diameter/2)**2*0.020/2.0
        self.diameter = float(diameter)
        self.mass = float(mass)
        self.mom_arm = self.diameter/2**1.5
        self.com_shift = centre_of_mass_shift
        self.r = self.diameter/2
        self.pr = self.prop_diameter/2
        self.cyl_ax = self.r - self.pr
        self.pos = pos
        self.fw = self.pr/35
        self.leg_length = self.diameter/4
        self.controller = None
        self.av = visual.vector(0,0,0)
        self.vv = visual.vector(0,0,0)
        self._last_recalc = None

        #Create visual image of the quad
        self.reset_rotation()
        self.props = [visual.ring(thickness=self.fw,
                             radius=self.pr, color=color.blue) for e in xrange(4)]
        self.propsc = [visual.cylinder(thickness=self.fw,
                             radius=self.pr-self.fw, color=(0,0,0), opacity=0.23) for e in xrange(4)]
        self.propsm = [visual.cone(radius=self.fw*3, color=color.blue) for e in xrange(4)]
        self.cyls = [visual.cylinder(pos=pos, radius=self.fw*2,
                                     color=color.blue) for e in xrange(4)]
        for p, c, m in zip(self.props[:2], self.cyls[:2], self.propsm[:2]):
            p.color = c.color = m.color = color.red
        self.sphere = visual.sphere(pos=pos, radius=self.fw*8, color=color.blue)
        self.legs = [visual.cylinder(pos=pos, radius=self.fw*1.5, color=color.green) for e in xrange(2)]
        # legs touching ground
        self.glegs = [visual.cylinder(pos=pos, radius=self.fw*1.5, color=color.green) for e in xrange(2)]
        self.recalc_axis()
        self.render()

    def reset_rotation(self):
        self.pdirs= [visual.vector(1,0,0), visual.vector(0,1,0)]
        self.perp = visual.cross(*self.pdirs)

    def render(self):
        # Leg rendering...
        span = (self.pdirs[0] - self.pdirs[1])/(2/self.leg_length)
        length = -self.perp*self.leg_length
        fspan = (self.pdirs[0] + self.pdirs[1])*self.leg_length
        self.legs[0].axis = span+length
        self.legs[1].axis = -span+length
        for l, gl in zip(self.legs, self.glegs):
            gl.axis = fspan
            l.pos = self.pos
            gl.pos = l.pos + l.axis - fspan/2
        # Propeller  and support rendering....
        for d, p, c, w, m in zip(reversed(self.pdirs), self.props[:2], self.cyls[:2], self.propsc[:2], self.propsm[:2]):
            p.pos = w.pos = m.pos = self.pos + d*self.r
            p.axis = self.perp
            w.axis = self.perp * (self.fw/2)
            m.axis = self.perp * (self.fw*3)
            c.axis = d*self.cyl_ax
            c.pos = self.pos
        for d, p, c, w, m in zip(reversed(self.pdirs), self.props[2:], self.cyls[2:], self.propsc[2:], self.propsm[2:]):
            p.pos = w.pos = m.pos = self.pos - d*self.r
            p.axis = self.perp
            c.axis = -d* self.cyl_ax
            w.axis = self.perp * (self.fw/2)
            m.axis = self.perp * (self.fw*3)
            c.pos = self.pos
        self.sphere.pos = self.pos

    def rotate(self, ang, axis=None):
        for e in (0, 1):
            self.pdirs[e] = visual.rotate(self.pdirs[e], ang, self.perp if axis is None else to_vec(axis)).norm()
        if axis is not None:
            self.perp = visual.cross(*self.pdirs).norm()
        self.recalc_axis()

    def recalc_axis(self):
        self.axis = (self.pdirs[0]-self.pdirs[1])/2.0, (self.pdirs[0]+self.pdirs[1])/2.0, self.perp


    def move(self, vec):
        vec = to_vec(vec)
        self.pos += vec
        scene.center = self.pos
        if self.pos[2]<self.leg_length:
            if self.vv.mag>1:
                scene.background = (1,0.6,0.4)
                if self.vv.mag>7:
                     raise Exception("CRAZY LANDING AT %d km/h" % int(self.vv.mag*3.6))
                else:
                    raise Exception("DANGEROUS LANDING AT %d km/h" % int(self.vv.mag*3.6))
            else:
                scene.background = (0.4, 1 ,0.4)
            raise Exception('Sage landing :)')

    def set_controller(self, controller):
        self.controller = controller(self)

    def update_motors(self):
        if self.controller is None:
            raise ValueError('You have to set the controller first!')
        powers = self.controller.get_powers()
        for power, motor in zip(powers, self.motors):
            motor.req_thrust(power)

    def get_acceleration(self):
        a, at = self.motors[0].get_thr_tor()
        b, bt = self.motors[1].get_thr_tor()
        c, ct = self.motors[2].get_thr_tor()
        d, dt = self.motors[3].get_thr_tor()
        AX = (a+b-c-d)*self.mom_arm/self.inertiaX
        AY = (a-b-c+d)*self.mom_arm/self.inertiaX
        AZ = -(at+bt+ct+dt)/self.inertiaZ
        HZ = (a+b+c+d)/self.mass + visual.dot(G, self.axis[2])
        return HZ, AX, AY, AZ

    def get_total_acc(self):
        HZ, AX, AY, AZ = self.get_acceleration()
        ANG = AX*self.axis[0] + AY*self.axis[1] + AZ*self.axis[2]
        A = (HZ-visual.dot(G, self.axis[2]))*self.axis[2] + G
        return ANG, A

    def recalc_speeds(self):
        if self._last_recalc is None:
            self._last_recalc = time.time()
        AA, VA = self.get_total_acc()
        dt = time.time() - self._last_recalc
        self._last_recalc = time.time()
        self.av += dt*AA
        self.vv += dt*VA




class Motor:
    def __init__(self, max_power, max_trust, prop_diameter, prop_mass, tr2to=60.0, pos_tor=True, delay=0.3):
        """
            max_trust is the max trust that a single motor can produce
            max_power is the max power of the motor
            prop_diameter - diameter of the propeller in inches
            prop_mass - mass of the propeller
        """
        self.frac = 0
        self.prop_diameter = float(prop_diameter)
        self.prop_mass = float(prop_mass)
        self.max_power = float(max_power)
        self.max_thrust = float(max_trust)
        self.tr2to = float(tr2to)
        self.pos_tor = pos_tor
        self.thrust = 0
        self.rthrust = 0
        self.rtime = time.time()
        self.delay = delay
        self.fault = 1+(random.random()-0.5)*0.00

    def req_thrust(self, thrust, throw=True):
        if abs(thrust)>self.max_thrust and throw:
            raise ValueError('INVALID THRUST', thrust)
        self.thrust = self.get_thrust()
        self.rthrust = min(max(thrust, -self.max_thrust), self.max_thrust)
        self.rtime = time.time()

    def get_thrust(self):
        pct = min((time.time() - self.rtime)/(self.delay*abs(self.thrust-self.rthrust+1e-20)/self.max_thrust),1)
        return (self.thrust + pct*(self.rthrust - self.thrust)) * self.fault


    def get_torgue(self):
        return self.get_thrust()/self.tr2to*(1.0 if self.pos_tor else -1.0)

    def get_thr_tor(self):
        t = self.get_thrust()
        return t, t/self.tr2to*(1.0 if self.pos_tor else -1.0)


PRINTED = False
X = visual.vector(1,0,0)
Y = visual.vector(0,1,0)
Z = visual.vector(0,0,1)

def stat_updater():
    delay = 1
    feed = updater.status_seq
    while True:
        while feed:
            status = feed.popleft()
            show = status['t'] + delay
            dif = show-time.time()
            if dif>0:
                print dif
                visual.sleep(dif)
            else:
                print "LATE"
            show_status(status)
        visual.sleep(0.01)


def show_status(status):
    r, p, y = status["fusionPose"]
    q.reset_rotation()
    q.rotate(p, X)
    q.rotate(r, Y)
    q.rotate(y, Z)
    q.render()





q = Quad()
z = visual.vector(0,0,1)
q.pos = visual.vector(0,0,0)
q.render()

link = Link(quad=False)
# IN handlers
out_handlers = [OutCommander()]
# OUT handlers - they will be accessed directly so they need to have separate names
messenger = InInfo(None)
updater = InStatus(None, on_status_update=None )
in_handlers = [messenger, updater]
# Initialise posts, they will not be called directly.
in_post = InPost(link, handlers=in_handlers)
out_post = OutPost(link, handlers=out_handlers)
out = Thread(target=in_post._handle_loop)  # executes commands from master
inp = Thread(target=out_post._handle_loop)  # sends important parameters to the master
out.daemon = inp.daemon = True
out.start()
inp.start()

stat_updater()
