from Feature import *
import threading
import Region
import Camera
import cv2
import time
import os
'''
I.  You need to complete two functions: position, ideal
II. In position(), you need to apply your algorithm, if no result or no existence, you should append
    (None..) to self.pos, else you append your result.
    (Pay attention: There is a check in Feature.py to run your position function twice for a single 
    image. If these positions are seperated seriously, the result will fail)
III.In ideal(), you should judge whether the current image is ideal so that we can amplify the camera to 
    get high-resolution image to give you for further process.
IV. You could add your class variables as you want
V.  If you want to print information, use logging:
        self.log.info("name: message")
        self.log.warn("name: message")
    The screen will only show warning information.
'''
cwd = os.getcwd()
NUM_THREADS = 1 # specialize for plate since written in another language, no direct I/O so we have to use file I/O, which may make problems.

class Plate(feature):
    def __init__(self,name='plate',num_threads=3,position=[0.0,0.0,0.0], log=None):
        feature.__init__(self, num_threads, \
                         Region.region(position=position, tar_pos=[-1.0,0.5,0.0], radius=[0.1,0.1,0.1]), \
                         Camera.camera(angle=[0.0,0.0]), name, log)
        self.ret.name=name
        self.num_threads=3
        self.log=log
        # define your variables
        pass

    # pay attention: before we call this function, self.pos should be set to empty
    def position(self, image, arg0=None, arg1=None, arg2=None):
        cv2.imwrite("./modules/plate/resources/image/plate.jpg", image)

        try:
            os.chdir(cwd+"/modules/plate")
            os.system("plate_detect.exe")
        except:
            os.chdir(cwd)
            self.log.error("Meet error when executing plate_detect.exe")
            return
        finally:
            os.chdir(cwd)
            self.log.info("The plate is being detected!")

        # detect whether it is finished; if finished, continue
        begin_time = time.time()
        while str(os.system("tasklist|find /i \"plate_detect.exe\"")) != '1': time.sleep(1.0)
        end_time = time.time()
        used_time = round(end_time-begin_time,2)
        self.log.info("Use "+str(used_time)+" seconds to locate the plate")

        with open(cwd+"/modules/plate/words.txt") as wordsFile:
            words = wordsFile.readline()
            if len(words)==0:
                self.ret.exist=False
                self.log.info("No plate is detected in the image!")
            elif len(words)<=4:
                self.ret.exist=True
                self.ret.ideal=False
            else:
                self.log.info("Plate number is detected successfully!")
                self.ret.exist=True

        # judge whether the feature exist
        if self.ret.exist is False:
            return

        # return the target position
        with open(cwd+"/modules/plate/position.txt") as posFile:
            line = posFile.readline()
            rect_string = line.split(" ")
            for i in range(len(rect_string)):
                rect_string[i]=int(rect_string[i])
            x, y, width, height = rect_string

        self.pos.append([x,y,x+width,y+height])
        self.ret.image=cv2.imread(cwd+"/modules/plate/result_graph.jpg")

    # before we call it, make sure you have something in the self.pos array
    def ideal(self, image, rect):
        # define your method
        width=image.shape[0]
        height=image.shape[1]
        channels=image.shape[2]
        try:
            assert(len(self.pos)>0)
        except:
            self.log.info("The length of detected position is 0. No way to test if ideal")
            return False

        if 1.0*(rect[0]+rect[2]/2-width/2)/width>PLATE_CENTER_BIAS or \
                                        1.0*(rect[1]+rect[3]/2-height/2)/height>PLATE_CENTER_BIAS:
            self.log.info("Plate Center Bias is unacceptable to be ideal!")
            return False
        if 1.0*rect[2]/width<PLATE_PHOTO_RATE or 1.0*rect[3]/height<PLATE_PHOTO_RATE:
            self.log.info("Plate photo accounts too small part in the image!")
            return False

        return True

    # no need to change
    def multi_detect(self,image):
        # change directory (not allowed in multi-process)
        try:
            os.chdir("./modules/plate")
        except:
            self.log.error("Check your environment path variables!")
            return
        finally:
            pass

        self.pos, threads=[],[]
        [threads.append(threading.Thread(target=self.position, args=([image]))) for i in range(NUM_THREADS)]
        for t in threads:
            t.setDaemon(True)
            t.start()
        for t in threads:
            t.join()

    # should return [relative_region_position, relative_camera_position]
    def translate(self, image, ret, region, camera):
        img_width = image.shape[0]
        img_height = image.shape[1]
        distance = [(ret.region[0]+ret.region[2])/2-img_width/2, (ret.region[1]+ret.region[3])/2-img_height/2]
        distance = [distance[0]/img_width, distance[1]/img_height]
        wid_rate = (region.center[0]-region.cubePoint[0][0]+XAXIS_INNER_DISTANCE)*PLATE_PROPORTION*distance[0]
        hei_rate = (region.center[0]-region.cubePoint[0][0]+XAXIS_INNER_DISTANCE)*PLATE_PROPORTION*distance[1]
        movement = [0.0, hei_rate, wid_rate] # this is because image coordinate is different
        for i in range(3):
            movement[i]+=region.center[i]
            movement[i]=float('%.2f' % movement[i])
        return [movement, camera.angle+[0.0,0.0]]

    def postprocess(self, image):
        pass

