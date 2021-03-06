from tkinter import *
from flex_thread import Thread
from twisted.internet import reactor, tksupport
from threading import Lock
import Region, Camera, Communicate, loginfo, GUI
import time, math, cv2
import numpy as np
from parameters import *


# check connect each time
# check battery each time

class UAV:
    # priority: MAN>SEARCH>DEFAULT
    MODE = SEARCH  # this define the control power of the plane.
    stop_signal = False
    MATRIX = np.eye(4)  # unit matrix

    def __init__(self):
        # initial parameters
        self.feature_queue = []
        self.root = Tk()
        self.gui = GUI.GUI(self.feature_queue, self.root)
        self.gui.recordMaster(self)
        self.gui.MODE = self.MODE

        self.log = loginfo.log(self.gui)
        self.log.info('GUI has been initialized.')
        self.gui.setLog(self.log)

        # setup connection with APP
        tksupport.install(self.root)
        self.comm = Communicate.communication()
        self.comm.setLog(self.log)
        self.listenBegin()

        self.region = Region.region(position=[-1.0, 1.0, -1.0], log=self.log)
        self.camera = Camera.camera(angle=[0.0, 0.0])
        # initialize region center and camera center

        # thread control center
        self.threadStart()

        self.log.info('Three Mode could be started!')
        self.log.info('Current Mode is ' + self.MODE + ' Mode.')
        self.log.info('Please INIT the coordinate system!')

        self.periodicCall()

        reactor.run()

    def periodicCall(self):
        self.root.after(200,self.periodicCall)
        self.gui.processInfo()

    # fix: input LF, RF, RB, LB, and FINISHANCHOR to end
    def anchorMatrix(self):
        # assert (self.comm.checkComm())
        self.log.info('Please put UAV at four anchor point: ')
        self.log.info('Need at least one at earth and one at 1M height')
        homelocation = self.comm.clients[0].homelocation
        '''
        homelocation = [
            [3442390.962775,7.100000,13473049.827100],
            [3442386.571666,7.300000,13473054.160324],
            [3442383.687167,2.700000,13473044.368006],
            [3442387.200889,2.600000,13473042.405330]]
        '''
        pos = homelocation
        dx0, dz0 = pos[0][0] - pos[3][0], pos[0][2] - pos[3][2]
        dx2, dz2 = pos[2][0] - pos[3][0], pos[2][2] - pos[3][2]

        self.MATRIX[0, 0], self.MATRIX[0, 2], self.MATRIX[0, 3] = \
            dx0 / SR_LENGTH, dx2 / SR_WIDTH, dx2 / 2 + pos[3][0]
        self.MATRIX[2, 0], self.MATRIX[2, 2], self.MATRIX[2, 3] = \
            dz0 / SR_LENGTH, dz2 / SR_WIDTH, dz2 / 2 + pos[3][2]

        self.MATRIX = np.mat(self.MATRIX)
        if self.MATRIX.I is None:
            self.log.error('The anchored matrix has no reverse matrix')
        self.log.info("UAV coordinate system has been anchored!")
        self.comm.setMatrix(self.MATRIX, self)

    def listenBegin(self, args=None):
        self.comm.clients = []
        reactor.listenTCP(80, self.comm)
        self.log.info('Reactor has began listened to 80.')

    # control target thread to start
    def threadStart(self):
        self.visitList, self.modeList = {}, {}

        self.center = Thread(target=self.modeCenter, args=(None,))
        # self.center.setDaemon(True)

        # start default visit mode for plane
        self.defaultVisit = Thread(target=self.defaultMode, args=(None,))
        self.defaultVisit.setDaemon(True)

        self.debugVisit = Thread(target=self.debugMode, args=(None,))
        self.debugVisit.setDaemon(True)

        self.searchVisit = Thread(target=self.searchMode, args=(None,))
        self.searchVisit.setDaemon(True)

        self.visitList[DEBUG] = self.debugVisit
        self.visitList[SEARCH] = self.searchVisit
        self.visitList[DEFAULT] = self.defaultVisit
        self.modeList[DEBUG] = self.debugMode
        self.modeList[SEARCH] = self.searchMode
        self.modeList[DEFAULT] = self.defaultMode
        self.visitList[self.MODE].start()

        self.center.start()  # start at last since all parameters are added into visitlist

    # if not used or meet error when running, begin default mode
    def defaultMode(self, args=None):  # abandon access to MODE
        while not self.stop_signal:
            while self.gui.pause: time.sleep(0.1)
            time.sleep(2.0)
            # reset target randomly
            random_region = self.region.getRandomRegion()
            random_angle = self.camera.getRandomAngle()
            pos = self.region.reach(random_region)
            angle = self.camera.reach(random_angle)
            arrive = self.comm.waitMove(pos, angle, "Default mode auto movement...")
            if arrive:
                self.region.setCenter(pos)
                self.camera.setCenter(angle)
            image = self.comm.waitImage(COMPRESS)
            self.gui.showImage(image, "default")

    # if feature was detected in queue and run search mode
    def searchMode(self, args=None):  # abandon access to MODE
        while not self.stop_signal:
            # begin detect mode
            while self.gui.pause: time.sleep(0.1)
            while len(self.gui.feature_queue) == 0: time.sleep(0.1)
            feature = self.gui.feature_queue.pop(-1)
            self.log.info("New feature " + feature.name + " asks for detection!")

            if self.MATRIX is None:
                self.log.info("Matrix has not been initialized!")
                return
            if len(self.comm.clients) == 0:
                self.log.info("Lost connection with UAV; please check the connection")
                return
            # current_position = self.MATRIX.I*self.comm.getPos()
            # self.region.setCenter(current_position)
            self.region.setTarget(feature.region.tar_pos)
            self.camera.setTarget(feature.camera.tar_angle)

            while self.MODE == SEARCH:
                while self.gui.pause: time.sleep(0.1)
                # blocked until there exists inqueue features
                while True:
                    pos = self.region.reach(feature.region.tar_pos)
                    angle = self.camera.reach(feature.camera.angle)

                    arrive = self.comm.waitMove(pos, angle, "UAV is approaching targeted position!")
                    if arrive:
                        self.region.setCenter(pos)
                        self.camera.setCenter(angle)
                    if pos == feature.region.tar_pos: break

                self.log.info("UAV has arrived at feature target location")
                image = self.comm.waitImage(COMPRESS)
                self.gui.centerImageQueue.append(image)
                ret = feature.img_pipe(image)  # this is the return info (format see Feature.py)
                allcount = 0
                if ret.exist is True:
                    while self.MODE == SEARCH and ret.ideal is False and allcount<2:
                        # decipher image information with return_info
                        allcount += 1
                        self.log.info('Correcting the position...')
                        reachInfo = feature.translate(image, ret, self.region, self.camera)
                        self.region.setTarget(reachInfo[0])
                        self.camera.setTarget(reachInfo[1])
                        pos = self.region.reach()
                        angle = self.camera.reach(angle)
                        arrive = self.comm.waitMove(pos, angle, \
                                                    "Search mode is adjusting position for feature " \
                                                    + feature.name)
                        if arrive:
                            self.region.setCenter(pos)
                            self.camera.setCenter(angle)

                        image = self.comm.waitImage(COMPRESS)
                        self.gui.centerImageQueue.append(image)
                        # recheck the result until ideal
                        ret = feature.img_pipe(image)

                    self.gui.imageQueue.append([ret.image, feature.name])
                    self.log.info("The situation is ideal. Further process is being executed.")
                    feature.postprocess(image)  # post process like storage or else
                    break  # wait for next feature coming in
                else:
                    self.log.info("No feature of " + feature.name + " is detected in current region.")
                    self.log.info("Please input specified new region to overwrite preset region.")
                    # region = self.executeCommand()
                    # feature.region.setTarget(ret.region)

    # used for early debug as well as reach the position when no detect in target position
    def debugMode(self, args=None):  # abandom access to MODE
        while not self.stop_signal:
            while self.gui.pause: time.sleep(0.1)
            if self.gui.messageInfo != '':
                lock = Lock()
                lock.acquire()
                command = self.gui.messageInfo
                command = command[:len(command) - 1]
                # command[-1]='\0' # delete the \n to simplify debuginfo
                self.gui.messageInfo = ''
                lock.release()

                arg = command.split(':')
                if arg[0] == "MOV":
                    temp = arg[1].split(',')
                    pos = [0.0,0.0,0.0]
                    for i in range(3): pos[i] = float(temp[i])
                    self.comm.waitMove(pos, self.camera.angle)
                    pos = self.region.reach(pos)
                    angle = self.camera.reach(self.camera.angle)
                    arrive = self.comm.waitMove(pos, angle, "Default mode auto movement...")
                    if arrive:
                        self.region.setCenter(pos)
                        self.camera.setCenter(angle)

                self.log.info('EXECUTE ' + command)

    # thread center used to control each mode to restart or terminate
    def modeCenter(self, args=None):
        while True:
            if sum(self.gui.CORNER) == 4:
                time.sleep(1.0)
                self.anchorMatrix()
                self.log.info('All four corners have been recorded.')
                self.gui.CORNER = [100.0,0.0,0.0,0.0]
            if self.gui.suspend is True:
                # suspend the plane
                if self.visitList[self.MODE].isAlive():
                    self.visitList[self.MODE].terminate()
                    self.visitList[self.MODE].join()
                    self.log.warn("Forced to suspend! Wait for further instruction!")
                continue
            '''
            if self.MODE == self.gui.MODE and self.visitList[self.MODE].isAlive() is False:
                try:
                    self.visitList[self.gui.MODE] = Thread(target=self.modeList[self.gui.MODE], args=(None,))
                    self.visitList[self.gui.MODE].start()
                except:
                    self.gui.insertLogInfo('Non-existing MODE name; ' + self.gui.MODE)
                self.log.info('Mode' + self.MODE + ' is started ')
            '''
            if self.MODE != self.gui.MODE:
                if self.visitList[self.MODE].isAlive():
                    self.visitList[self.MODE].terminate()
                    self.visitList[self.MODE].join()
                if self.gui.suspend is True: continue
                assert (not self.visitList[self.MODE].isAlive())
                try:
                    self.visitList[self.gui.MODE] = Thread(target=self.modeList[self.gui.MODE], args=(None,))
                    self.visitList[self.gui.MODE].start()
                except:
                    self.gui.insertLogInfo('Non-existing MODE name; ' + self.gui.MODE)
                self.log.info('Mode is changed from ' + self.MODE + ' to ' + self.gui.MODE)
                self.MODE = self.gui.MODE


if __name__ == '__main__':
    uav = UAV()
