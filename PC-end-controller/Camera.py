import numpy as np

class camera:
    Relative=[0.0,0.0,0.0] # relative position to the plane
    def __init__(self,angle=[0.0,0.0], tar_angle=[0.0,0.0],comm=None):
        self.angle=angle # self.angle is [yaw, pitch]
        self.tar_angle=tar_angle
        self.comm=comm
        self.transformMatrix=None
        # self.comm.setangle()

    def setTarget(self, tar_angle):
        self.tar_angle = tar_angle

    def setCenter(self, angle):
        self.angle = angle

    # reach
    def reach(self, pos):
        return pos

    def getRandomAngle(self):
        return [np.random.random()*180.0, np.random.random()*(0.0-90.0)]
