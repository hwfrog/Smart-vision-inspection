from tkinter import *
import os, time
import plate
import ancheck
from parameters import *
from PIL import ImageTk, Image
from matplotlib import pyplot as plt
import cv2
from twisted.internet import *

class GUI(Frame):
    def __init__(self, feature_queue, master=None):
        # duties: initial the software , welcome window
        Frame.__init__(self, master)
        self.log = None
        self.master.title('Detect Plane')
        self.initInterface(master)
        self.interface()  # used for outer space to receive information
        self.feature_queue = feature_queue
        self.UAV = None # record the UAV self
        os.chdir(cwd+"/log/images")
        os.system("del /f /s /q *")
        os.chdir(cwd)
        # self.mainloop(0)

    def setLog(self, log):
        self.log = log

    def recordMaster(self, UAV):
        self.UAV=UAV

    def initInterface(self, master=None):
        self.panedwindow = PanedWindow(master, orient=VERTICAL)
        self.panedwindow.pack(fill=BOTH, expand=1)

        self.up = PanedWindow(self.panedwindow, orient=HORIZONTAL)
        self.panedwindow.add(self.up, width=5 * UNIT_WID, height=2 * UNIT_HEI + HEAD_HEI)
        self.panedwindow.add(Label(self.panedwindow, bg='gray'), height=LINE_WID)
        self.down = PanedWindow(self.panedwindow, orient=HORIZONTAL)
        self.panedwindow.add(self.down, width=5 * UNIT_WID, height=1 * UNIT_HEI)
        self.panedwindow.add(Label(self.panedwindow, bg='gray'), height=LINE_WID)
        command = PanedWindow(self.panedwindow, orient=HORIZONTAL)
        self.panedwindow.add(command, width=5 * UNIT_WID, height=HEAD_HEI)

        self.image = PanedWindow(self.up, orient=HORIZONTAL)
        self.up.add(self.image, width=3 * UNIT_WID, height=2 * UNIT_HEI)
        self.up.add(Label(self.up, bg='gray'), width=LINE_WID)
        labels = PanedWindow(self.up, orient=HORIZONTAL)
        self.up.add(labels, width=2 * UNIT_WID, height=2 * UNIT_HEI)

        label_left = PanedWindow(labels, orient=VERTICAL)
        labels.add(label_left, width=UNIT_WID, height=2 * UNIT_HEI)
        labels.add(Label(labels, bg='gray'), width=LINE_WID)
        label_right = PanedWindow(labels, orient=VERTICAL)
        labels.add(label_right, width=UNIT_WID, height=2 * UNIT_HEI)

        # interface: loginfo, planeinfo, feature, buttons
        loginfoHead = Label(label_left, bg='gray', text='LOG INFO', anchor=W)
        label_left.add(loginfoHead, width=UNIT_WID, height=HEAD_HEI)
        self.loginfo = StringVar()
        loginfo = Label(label_left, textvariable=self.loginfo, wraplength=UNIT_WID, justify=LEFT, bg='white', anchor=NW)
        label_left.add(loginfo, width=UNIT_WID, height=UNIT_HEI - HEAD_HEI)
        label_left.add(Label(label_left, bg='gray'), height=LINE_WID)

        # feature part, checkbox
        featureHead = Label(label_left, bg='gray', text='FEATURES', anchor=W)
        label_left.add(featureHead, width=UNIT_WID, height=HEAD_HEI)
        self.feature = PanedWindow(label_left, orient=VERTICAL)
        label_left.add(self.feature, width=UNIT_WID, height=UNIT_HEI - HEAD_HEI)
        self.lcMark = IntVar()  # license number mark
        checklc = Checkbutton(self.feature, text='License Plate', variable=self.lcMark, anchor=NW)
        checklc.deselect()
        self.feature.add(checklc, width=UNIT_WID, height=HEAD_HEI)
        self.acMark = IntVar()  # annual check mark
        checkac = Checkbutton(self.feature, text='Annual Check', variable=self.acMark, anchor=NW)
        checkac.deselect()
        self.feature.add(checkac, width=UNIT_WID, height=HEAD_HEI)

        # plane info part, add scroll
        # what does plane info need: position, velocity, distance to saferegion
        planeinfoHead = Label(label_right, bg='gray', text='PLANE INFO', anchor=W)
        label_right.add(planeinfoHead, width=UNIT_WID, height=HEAD_HEI)
        planeinfo = PanedWindow(label_right, orient=VERTICAL)
        label_right.add(planeinfo, width=UNIT_WID, height=UNIT_HEI - HEAD_HEI)
        planeinfoUp = PanedWindow(planeinfo, orient=HORIZONTAL)
        piYScroll = Scrollbar(planeinfoUp, orient=VERTICAL)
        piXScroll = Scrollbar(planeinfo, orient=HORIZONTAL)
        self.planeinfo = Listbox(planeinfoUp, xscrollcommand=piXScroll.set, yscrollcommand=piYScroll.set)
        planeinfo.add(planeinfoUp, width=UNIT_WID, height=UNIT_HEI - HEAD_HEI - BAR_WID)
        planeinfoUp.add(self.planeinfo, width=UNIT_WID - BAR_WID * 3, height=UNIT_HEI - HEAD_HEI - BAR_WID)
        planeinfoUp.add(piYScroll, width=BAR_WID, height=UNIT_HEI - HEAD_HEI - BAR_WID)
        planeinfo.add(piXScroll, width=UNIT_WID - BAR_WID, height=BAR_WID)
        piXScroll['command'] = self.planeinfo.xview
        piYScroll['command'] = self.planeinfo.yview

        label_right.add(Label(label_right, bg='gray'), height=LINE_WID)

        buttonsHead = Label(label_right, bg='gray', text='CONSOLE', anchor=W)
        label_right.add(buttonsHead, width=UNIT_WID, height=HEAD_HEI)
        self.buttons = PanedWindow(label_right, orient=VERTICAL)
        label_right.add(self.buttons, width=UNIT_WID, height=UNIT_HEI - HEAD_HEI)

        # add buttons ( pay attention you need to fix below two paragraphs)
        self.buttonInit = Button(self.buttons, text='INIT', command = self.initMatrixCommand)
        self.buttonDetect = Button(self.buttons, text='DETECT', command=self.detectCommand)
        self.buttonPause = Button(self.buttons, text='PAUSE',
                                  command=self.pauseCommand)  # it will be able to continue after it starts
        self.buttonSuspend = Button(self.buttons, text='SUSPEND', command=self.suspendCommand)
        self.buttonExit = Button(self.buttons, text='EXIT', command=self.guiExit)
        tHeight = int((UNIT_HEI - HEAD_HEI) / NUM_BUTTONS)

        self.buttons.add(self.buttonInit,width=UNIT_WID,height=tHeight)
        self.buttons.add(self.buttonDetect, width=UNIT_WID, height=tHeight)
        self.buttons.add(self.buttonPause, width=UNIT_WID, height=tHeight)
        self.buttons.add(self.buttonSuspend, width=UNIT_WID, height=tHeight)
        self.buttons.add(self.buttonExit, width=UNIT_WID, height=tHeight)

        # Add detected photos
        self.detectImages = PanedWindow(self.down, orient=HORIZONTAL)
        self.down.add(self.detectImages, width=5 * UNIT_WID, height=UNIT_HEI)

        # send command lines
        command.add(Label(command, bg='red', text='COMMAND: ', anchor=W), width=UNIT_WID / 2)
        self.command = Text(command)
        command.add(self.command, width=UNIT_WID * 4)
        self.buttonCommand = Button(command, text='ENTER', command=self.readCommand)
        command.add(self.buttonCommand, width=UNIT_WID / 2)

        self.result_images=[None for i in range(NUM_BOTTOM_IMAGES)]
        for i in range(len(self.result_images)):
            self.result_images[i] = Label(self.detectImages, bg='gray', text='NONE PICTURE', anchor=CENTER)
            self.detectImages.add(self.result_images[i], width=UNIT_WID, height=UNIT_HEI)


        return

    def interface(self):
        self.messageInfo = ''
        self.imageInfo = None
        self.buttonInfo = False
        self.MODE = None
        self.pause = True
        self.suspend = False
        self.num_images=0 # record how many images have been saved

    # called every 200ms so that it can be updated in main thread
    info = ''
    def processInfo(self):
        self.loginfo.set(self.info)
        self.messageInfo = self.command.get('1.0', END)
        self.messageInfo = self.messageInfo[:-1]

    LOG_INFO = ['\n' for i in range(LOGINFO_LINE_LIMIT)]

    def insertLogInfo(self, string):
        self.LOG_INFO.append(string)
        if len(self.LOG_INFO) > LOGINFO_LINE_LIMIT: self.LOG_INFO.pop(0)
        self.info = ''
        for i in range(LOGINFO_LINE_LIMIT):
            self.info += self.LOG_INFO[i]
        # self.loginfo.set(self.info)
        with open(LOGINFO_PATH, 'a') as log_file:
            log_file.write(string)

    def initMatrixCommand(self):
        self.UAV.anchorMatrix(self.UAV.comm.clients.homelocation)
        self.UAV.comm.setMatrix(self.UAV.MATRIX)

    CORNER = [0,0,0,0]
    CORNER_NAME = ['LF','RF','RB','LB']
    homelocation = []
    def readCommand(self):
        temp = self.command.get('1.0', END)
        try:
            arg = temp.split(':')
            if arg[0] == 'MODE':
                temp = arg[1].split('\n')
                self.MODE = temp[0]
            elif arg[0] == 'REGION':
                temp=arg[1].split('\n')
                if temp[0] == 'SHOW':
                    self.log.info("Route is drawn...")
                    self.UAV.region.drawRoute()
                    plt.show()
            elif arg[0] == 'POS':
                temp = arg[1].split('\n')
                if temp[0] not in self.CORNER_NAME:
                    self.log.info('Input info has invalid anchor description.')
                    return
                for i in range(len(self.CORNER_NAME)):
                    if self.CORNER_NAME[i]==temp[0]:self.CORNER[i]=1
                for client in self.UAV.comm.clients:
                    temp_string = 'pos:'+temp[0]+':0:0:0:0'
                    client.transport.write(temp_string.encode('ascii'))
                    time.sleep(1.0)
            else:
                self.messageInfo = temp

            self.command.delete('1.0', END)
        except:
            self.log.error('Meet error when analyzing command!')

    def guiExit(self):
        os.remove(LOGINFO_PATH)
        exit(0)

    def pauseCommand(self):
        self.suspend = False
        self.pause = True

    def suspendCommand(self):
        self.suspend = True

    def detectCommand(self):
        self.pause = False
        self.suspend = False
        # it will wait until fronter feature is processed
        if self.lcMark.get() == 1:  # license number check
            self.feature_queue.append(plate.Plate(position=self.UAV.region.center,log=self.log))
            self.lcMark.set(0)

        if self.acMark.get() == 1:  # annual mark check
            self.feature_queue.append(ancheck.Ancheck(log=self.log))
            self.acMark.set(0)

    # show image in the ith structure (if image is None, clean all the image)
    num_images = 0
    all_images = 0
    temp_images=[]
    def showImage(self, image, name):
        if image is None:
            self.num_images=0
            for ele in self.result_images:
                ele = None
            return
        path = cwd + IMAGE_STORE_POSITION + name + str(self.all_images)+".jpg"
        cv2.imwrite(path,image) # save image to local space
        self.all_images+=1

        # temp_image = ImageTk.PhotoImage( \
        #    Image.fromarray(image).resize(UNIT_WID,UNIT_HEI))
        if self.num_images is NUM_BOTTOM_IMAGES:
            self.log.warn("The bottom image region has been filled! The new image will replace the first one")
            self.num_images=0

        temp_image = Image.open(path)
        height, width = temp_image.size
        if UNIT_HEI/height > UNIT_WID/width:
            width*=UNIT_HEI/height
            height = UNIT_HEI
        else:
            width = UNIT_WID
            height*=UNIT_WID/width
        width, height = int(width), int(height)
        self.temp_images.append(ImageTk.PhotoImage(temp_image.resize((width, height))))

        self.result_images[self.num_images].config(image=self.temp_images[-1])
        self.num_images+=1
