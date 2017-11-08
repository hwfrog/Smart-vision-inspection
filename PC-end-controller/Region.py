# This file will define the safe region for plane to move as well as define the movement
from parameters import *
import numpy as np
import log
import math

from matplotlib import pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

class safeRegion:
    def __init__(self):
        self.cubePoint = [None, None]
        self.cubePoint[1] = [SR_LENGTH, SR_HEIGHT, SR_WIDTH / 2]
        self.cubePoint[0] = [0.0, 0.0, -SR_WIDTH / 2]  # should assume ground at 0.0, z base is changeable
        self.vertices = []  # save all vertexes
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    self.vertices.append([self.cubePoint[i][0], self.cubePoint[j][1], self.cubePoint[k][2]])

    # if avoid safeRegion successfully, return True
    def avoidRegion(self, pos1, pos2):
        ret1, ret2 = 0, 0
        for i in range(3):
            if pos1[i] > self.cubePoint[0][i] and pos1[i] < self.cubePoint[1][i]: ret1 += 1
            if pos2[i] > self.cubePoint[0][i] and pos2[i] < self.cubePoint[1][i]: ret2 += 1
        if ret1 == 3 or ret2 == 3:return False
        for i in range(3):
            if pos1[i] == pos2[i]: continue
            if pos1[i] >= self.cubePoint[1][i] and pos2[i] >= self.cubePoint[1][i]: continue
            if pos1[i] <= self.cubePoint[0][i] and pos2[i] <= self.cubePoint[0][i]: continue

            box, t1, t2 = [], [], []
            for j in range(3):
                if j != i:
                    box.append(self.cubePoint[0][j])
                    box.append(self.cubePoint[1][j])
                    t1.append(pos1[j])
                    t2.append(pos2[j])

            for j in range(2):
                if (pos1[i] - self.cubePoint[j][i]) * (pos2[i] - self.cubePoint[j][i]) > 0: continue
                if j==0 and pos1[i]<=self.cubePoint[j][i] and pos2[i]<=self.cubePoint[j][i]: continue
                if j==1 and pos1[i]>=self.cubePoint[j][i] and pos2[i]>=self.cubePoint[j][i]: continue
                rate = (self.cubePoint[j][i] - pos1[i]) / (pos2[i] - pos1[i])
                if self.interBox(t1, t2, box, rate) == True:
                    return False

        n1,n2=0,0
        for i in range(3):
            if pos1[i]==self.cubePoint[0][i] or pos1[i]==self.cubePoint[1][i]:n1+=1
            if pos2[i]==self.cubePoint[0][i] or pos2[i]==self.cubePoint[1][i]:n2+=1
        if n1>=2 and n2>=2:
            count=0
            for i in range(3):
                if pos1[i]==pos2[i] and (pos1[i]==self.cubePoint[0][i] or pos1[i]==self.cubePoint[1][i]):
                    count+=1
            if count==0:return False
        return True

    # sub-function for avoidRegion
    def interBox(self, tp1, tp2, box, rate):
        target = [0, 0]
        target[0] = tp1[0] + (tp2[0] - tp1[0]) * rate
        target[1] = tp1[1] + (tp2[1] - tp1[1]) * rate
        if target[0] > box[0] and target[0] < box[1] and target[1] > box[2] and target[1] < box[3]:
            return True
        return False

    # return the distance between current position and safeRegion
    def distance(self, pos):
        m = [1e+5 for i in range(3)]
        for i in range(3):
            if (pos[i] - self.cubePoint[0][i]) * (pos[i] - self.cubePoint[1][i]) < 0:
                m[i] = 0
            else:
                m[i] = min([m[i], abs(pos[i] - self.cubePoint[0][i]), abs(pos[i] - self.cubePoint[1][i])])
                m[i] = m[i] * m[i]
        return math.sqrt(math.fsum(m))

    # draw the shape of safe region in 3D format
    def drawSafeRegion(self):
        fig=plt.figure()

        ax = Axes3D(fig)
        X = np.arange(0.0, SR_LENGTH+INTERVAL, INTERVAL)
        Y = np.arange(-SR_WIDTH/2, SR_WIDTH/2+INTERVAL, INTERVAL)
        X, Y = np.meshgrid(X, Y)
        Z = SR_HEIGHT
        ax.plot_surface(X, Y, Z, alpha=0.7)
        Z = 0.0
        ax.plot_surface(X, Y, Z, alpha=0.7)

        Z = np.arange(0.0, SR_HEIGHT+INTERVAL, INTERVAL)
        Y = np.arange(-SR_WIDTH / 2, SR_WIDTH / 2+INTERVAL, INTERVAL)
        Z, Y = np.meshgrid(Z, Y)
        X = 0.0
        ax.plot_surface(X, Y, Z, alpha=0.7)
        X = SR_LENGTH
        ax.plot_surface(X, Y, Z, alpha=0.7)

        Z = np.arange(0.0, SR_HEIGHT + INTERVAL, INTERVAL)
        X = np.arange(0.0, SR_LENGTH + INTERVAL, INTERVAL)
        X, Z = np.meshgrid(X, Z)
        Y = -SR_WIDTH/2
        ax.plot_surface(X, Y, Z, alpha=0.7)
        Y=SR_WIDTH/2
        ax.plot_surface(X, Y, Z, alpha=0.7)

        width = max([(self.cubePoint[1][i]-self.cubePoint[0][i])/2 for i in range(3)])
        mid = [(self.cubePoint[1][i]+self.cubePoint[0][i])/2 for i in range(3)]
        plt.xlim(mid[0]-ENLARGE*width,mid[0]+ENLARGE*width)
        plt.ylim(mid[1]-ENLARGE*width,mid[1]+ENLARGE*width)
        ax.set_zlim(mid[2]-ENLARGE*width,mid[2]+ENLARGE*width)
        return ax

    # return a random region between a certainly enlarged scale
    def getRandomRegion(self):
        pos=[0.0,0.0,0.0]
        for i in range(3):
            pos[i]=(np.random.random()-0.5)*2*(self.cubePoint[1][i]-self.cubePoint[0][i])
            if pos[i]>0: pos[i]+=self.cubePoint[1][i]
            if pos[i]<0: pos[i]+=self.cubePoint[0][i]
        pos[1]=np.random.random()+SAFE_HEIGHT+1.0
        return pos


class region(safeRegion):
    MATRIX = []  # this is the matrix relative to world matrix

    def __init__(self, position=[0.0,0.0,0.0], tar_pos = [0.0,0.0,0.0], radius=[1.0,1.0,1.0], log=None):
        safeRegion.__init__(self)
        self.info = ''  # record related information for debugging
        self.center = position
        self.tar_pos = tar_pos
        self.radius = radius
        self.log = log

    def setCenter(self, pos, radius=None):
        self.center = pos
        if radius is not None:
            self.radius = radius

    def setTarget(self, pos):
        self.tar_pos=pos

    # return the should-be target position if want to go to tar_position
    def reach(self, tar_region=None):
        if tar_region is None: tar_region=self.tar_pos
        if tar_region[1] <= 0:
            self.log.error('Wrong target position!')
            return None
        if self.avoidRegion(pos1=self.center, pos2=tar_region) == True:
            self.tar_pos=tar_region
            return tar_region
        else:
            tar_pos = [0.0, 0.0, 0.0]
            access, paccess = [], []
            for ele in self.vertices:
                # find vertices both of them can access
                start, end = self.avoidRegion(self.center, ele), self.avoidRegion(tar_region, ele)
                if start:
                    paccess.append(ele)
                    if end: access.append(ele)  # access for points having access to both point

            temp = []
            if len(access) == 0:
                # the case when on opposite region
                assert (len(paccess) == 4)
                for ele in paccess:
                    if ele[1] > 0.0:
                        temp.append(ele)
                assert (len(temp) == 2)
            else:
                for ele1 in access:
                    for ele2 in access:
                        count = 0
                        for i in range(3):
                            if ele1[i] == ele2[i]: count += 1
                        if count == 2 and not (
                                ele1[1] == 0.0 and ele2[1] == 0.0):  # on the same side and not on the ground
                            temp.append(ele1)
                            temp.append(ele2)
                            break
                    if len(temp) > 0: break

            if (len(temp) == 0):
                self.log.error('Cannot find path to the target, check the target position or the algorithm')
                return None

            for i in range(3):
                if temp[0][i] != temp[1][i]:
                    t1, t2 = temp[0][i], temp[1][i]
                    if (self.center[i] - t1) * (self.center[i] - t2) < 0:
                        tar_pos[i] = self.center[i]
                    elif abs(self.center[i] - t1) > abs(self.center[i] - t2):
                        tar_pos[i] = t2
                    else:
                        tar_pos[i] = t1
                else:
                    tar_pos[i] = temp[0][i]
            self.tar_pos=tar_pos
            return tar_pos

    def defaultVisit(self):
        if self.center[1]<MIN_HEIGHT:
            self.log.info('Height is too low.')

    # pay attention that the coordinate system is rotated (Input: (length, height, width))
    def drawRoute(self,color=(1.0,0.0,0.0)):
        self.ax=self.drawSafeRegion()
        if self.center==self.tar_pos:
            self.log.info("No desired target position!")
            return self.ax
        pos1, pos2=self.center,self.tar_pos
        # self.ax.plot(xs=[5.0, 4.0], ys=[0.3, 1.8], zs=[1.5, 1.2], marker='o', color=(1.0, 0.0, 0.0),linestyle='--')
        if self.avoidRegion(pos1,pos2) is True:
            self.ax.plot(xs=[pos1[0],pos2[0]], ys=[pos1[2],pos2[2]], zs=[pos1[1],pos2[1]], \
                         marker='o', color=(1.0,0.0,0.0), linestyle='--')
        else:
            self.log.warn("Current path might meet collision!")

        self.log.info("Current Position: "+str(pos1))
        self.log.info("Target Position: "+str(pos2))
        return self.ax


if __name__ == '__main__':
    r = region()
    r.setCenter([7.0, 1.5, 1.9])
    pos = r.reach([1.3, 0.8, 2.1])
    print(pos)
    ax = r.drawRoute()
    plt.show()

    r.setCenter(pos)
    print(r.reach([1.3, 0.8, -2.1]))
    ax = r.drawRoute()
    plt.show()
