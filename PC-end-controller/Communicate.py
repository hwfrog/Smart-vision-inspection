from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor
from PIL import ImageTk, Image
import scipy.misc
import numpy as np
import logging, time, os
import cv2,math
from parameters import *
from _openssl import *

class communication(Factory):
    matrix = None
    log = None
    UAV = None
    # wait until the UAV move to specific position (format pos:[0.0,0.0,0.0], angle:[0.0,0.0])
    def waitMove(self, ori_pos, angle, info=None):
        if self.matrix is None:
            self.log.info('Init the matrix before further process!')
            return None

        # calculate mid-point
        pos = []
        for i in range(3):pos.append(ori_pos[i])
        if pos[0]<=self.UAV.region.cubePoint[0][0]: pos[0] -= 1.0
        elif pos[0]>self.UAV.region.cubePoint[1][0]: pos[0] += 1.0
        elif pos[2]<self.UAV.region.cubePoint[0][2]: pos[2] -= 1.0
        elif pos[2]>self.UAV.region.cubePoint[1][2]: pos[2] += 1.0
        mid_target = np.zeros((4, 1))
        for i in range(3): mid_target[i][0] = pos[i]
        mid_target[3][0] = 1.0
        mid_target=self.matrix*mid_target
        mid_target = mid_target.getA()

        # calculate target position
        target = np.zeros((4,1))
        for i in range(3): target[i][0]=ori_pos[i]
        target[3][0] = 1.0
        target = self.matrix*target
        target = target.getA()
        # here target has the same coordinate system with UAV

        current_position = self.getPos()
        move = [0,0,0]
        for i in range(3): move[i] = target[i][0]-current_position[i]
        move[0] = move[0] * LATITUDE_TO_METER
        move[2] = move[2] * LONGITUDE_TO_METER

        for client in self.clients:client.iswping = True
        message =  "wp:" + str(target[0][0]) + ":" + str(target[1][0]) + ":" + str(target[2][0]) + ":" + str(
                angle[0]) + ":" + str(angle[1])+":"+str(mid_target[0][0])+":"+str(mid_target[2][0])

        self.log.info(self.printMove(move))
        client.transport.write(message.encode('ascii'))
        while client.iswping is True: time.sleep(0.1)
        return True

    def printMove(self, pos):
        if pos[0] > 0: string = "MOVE: to north " + str(round(pos[0],2)) + " meters, "
        elif pos[0] < 0: string = "MOVE: to south " + str(round(-pos[0],2)) + " meters, "
        if pos[2] > 0: string += "east " + str(round(pos[2],2)) + " meters, "
        elif pos[2] < 0: string += "west " + str(round(-pos[2],2)) + " meters, "
        if pos[1] > 0: string += "up " + str(round(pos[1],2)) + " meters."
        elif pos[1] < 0: string += "down " + str(round(-pos[1],2)) + " meters."
        return string

    # wait until image is received
    def waitImage(self, compression):
        for client in self.clients:
            client.image = open("plate.jpg",'wb')
            client.isdownloading = True
            temp_string = 'shoot:'+compression+':0:0:0:0'
            client.transport.write(temp_string.encode('ascii'))
            time.sleep(2.0)
            while client.isdownloading :
                time.sleep(0.1)
            client.image.close()
            client.image = None

        img = cv2.imread("plate.jpg")
        cv2.imwrite("./modules/plate/resources/image/plate.jpg",img)
        return img

    def getPos(self):
        for client in self.clients: client.iswping = True
        for client in self.clients:
            client.homelocation = []
            message = 'pos:LF:0:0:0:0'
            client.transport.write(message.encode('ascii'))
            while client.iswping is True: time.sleep(0.1)
        # return pos
        for client in self.clients: client.iswping = True
        return self.clients[0].homelocation[0]

    # check whether the communication is usable
    def checkComm(self):
        if self.clients == []:
            return False
        else:
            return True

    def setLog(self,log):
        self.log = log
    def takeoff(self):
        for client in self.clients:
            client.transport.write("takeoff:0:0:0:0:0")

    def land(self):
        for client in self.clients:
            client.transport.write("land:0:0:0:0:0")

    def initClient(self):
        self.clients = []

    def buildProtocol(self, addr):
        return communication_client(self, self.log)

    def shootphoto(self, compression):
        for client in self.clients:
            client.image = open("tmp.jpeg",'wb')
            client.isdownloading = True
            client.transport.write("shoot:"+compression+":xxx")
            while client.isdownloading :
                time.sleep(0.1)
            client.image.close()
            client.image = None

    def sendmessage(self, sentence):
        for client in self.clients:
            client.transport.write(sentence)

    def setMatrix(self, matrix, UAV):
        assert (matrix is not None)
        self.matrix = matrix
        self.UAV = UAV


class communication_client(Protocol):
    def __init__(self, factory, log=None):
        self.factory = factory
        self.images = {}
        self.image = None
        self.homelocation = []
        self.isdownloading = False
        self.iswping = False
        self.log = log

    def connectionMade(self):
        self.factory.clients.append(self)
        self.log.info('Client has been added!')

    def connectionLost(self, reason):
        self.factory.clients.remove(self)
        self.log.info('Client has been removed')

    def dataReceived(self, data):
        print(data)
        if (not self.isdownloading):
            clean_data = data.strip()
            clean_data = clean_data.decode('ascii')
            clean_data = clean_data.split(':', 3)
            if (len(clean_data) == 4):
                Type = clean_data[0]
                Name = clean_data[1]
                Content = clean_data[2]
                content2 = clean_data[3]
                if Type == "iam":
                    self.name = Name
                    msg = self.name + " has joined"
                elif Type == "msg":
                    msg = self.name + ": " + Name + "\n" + Content
                elif Type == "pos":
                    self.homelocation.append([float(Name), float(Content), float(content2)])
                    self.iswping = False
                elif Type == "cmd":
                    if Name == "close":
                        if Content in self.images:
                            self.images[Content].close()
                    elif Name == "wpfinish":
                    	self.iswping = False
        else:
            data = data.strip()
            if (data[-6:] == "finish".encode('ascii')):
                self.image.write(data[:-6])
                self.isdownloading = False
            else:
                self.image.write(data)
