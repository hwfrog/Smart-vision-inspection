from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor
from PIL import ImageTk, Image
import scipy.misc
import numpy as np
import logging, time, os
import cv2

class communication(Factory):
    matrix = None
    log = None
    # wait until the UAV move to specific position (format pos:[0.0,0.0,0.0], angle:[0.0,0.0])
    def waitMove(self, pos, angle, info=None):
        if self.matrix is None:
            self.log.info('Init the matrix before further process!')
            return None

        temp_pos = np.zeros((4,1))
        for i in range(3):temp_pos[i][0]=pos[i]
        temp_pos[3][0] = 1.0

        target = self.matrix*temp_pos

        # here target has the same coordinate system with UAV
        # here target has the same coordinate system with UAV
        for client in self.clients:
            client.iswping = True
        client.transport.write(
            "wp:" + str(target[0][0]) + ":" + str(target[1][0]) + ":" + str(target[2][0]) + ":" + str(
                angle[0][0]) + ":" + str(angle[1][0]))
        while client.iswping:
            time.sleep(0.1)

        time.sleep(1.0)
        return True

    # wait until image is received
    def waitImage(self, compression):
        for client in self.clients:
            client.image = open("plate.jpg",'wb')
            client.isdownloading = True
            client.transport.write("shoot:"+compression+":0:0:0:0")
            while client.isdownloading :
                time.sleep(0.1)
            client.image.close()
            client.image = None

        img = cv2.imread("plate.jpg")
        cv2.imwrite("./modules/plate/resources/image/plate.jpg",img)
        return img

    # wait until position is returned (here you need to give value to pos)
    def getPos(self):
        if self.matrix is None:
            self.log.info('Init the matrix before further process!')
            return None

        for client in self.clients:
            client.homelocation = None
            client.transport.write("getp:0:0:0:0:0")
            while not client.homelocation:
                time.sleep(0.1)
            pos = client.homelocation

        pos = self.matrix.I*pos
        return None

    # check whether the communication is usable
    def checkComm(self):
        if self.clients == []:
            return False
        else:
            return True

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

    def setMatrix(self, matrix):
        assert (matrix is not None)
        self.matrix = matrix

    def setLog(self, log):
        self.log = log


class communication_client(Protocol):
    def __init__(self, factory, log):
        self.factory = factory
        self.images = {}
        self.image = None
        self.homelocation = None
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
        if (not self.isdownloading):
            clean_data = data.strip()
            clean_data = clean_data.split(":", 2)
            if (len(clean_data) == 3):
                Type = clean_data[0]
                Name = clean_data[1]
                Content = clean_data[2]
                if Type == "iam":
                    self.name = Name
                    msg = self.name + " has joined"
                elif Type == "msg":
                    msg = self.name + ": " + Name + "\n" + Content
                elif Type == "pos":
                    self.homelocation = [float(Name), float(Content)]
                elif Type == "cmd":
                    if Name == "close":
                        if Content in self.images:
                            self.images[Content].close()
                    elif Name == "wpfinish":
                    	self.iswping = False
        else:
            data = data.strip()
            if (data[-6:] == "finish"):
                self.image.write(data[:-6])
                self.isdownloading = False
            else:
                self.image.write(data)
