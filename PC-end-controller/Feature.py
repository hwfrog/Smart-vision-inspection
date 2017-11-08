import cv2
import numpy as np
import log
import threading
from img_extras import *
from parameters import *

class Img_return:
    def __init__(self, name, exist=False, ideal=False, image=None, region=None):
        self.name = name
        self.exist = False
        self.useful = False
        self.ideal = False
        self.deltaTime=0.0
        self.image=None
        self.region = [None, None, None, None]  # left top + right bottom, w + h

    def reset(self):
        self.exist = False
        self.useful = False
        self.ideal = False
        self.deltaTime=0.0
        self.image=None
        self.region = [None, None, None, None]

# pay attention:
#       region: where you expect plane position to find the feature
#       camera: camera angle you expect to find faeture
#       translate: how to adjust according to ref
class feature:
    # class variables
    lastTime = 0.0

    def __init__(self, num_threads, region, camera, name, log):
        # self variables
        self.ret = Img_return(name=name)
        self.num_threads = 3
        self.region=region  # this should be your target position of UAV and target stable radius
        self.camera=camera # this defines the yaw, pitch of UAV
        self.name=name
        self.log=log
        self.pos=[] # this defines [x,y,width,height]. The region is [x,y,x+width,y+height]

    def position(self, image, arg0=None, arg1=None, arg2=None):
        self.pos.append([None, None, None, None])

    # this place should use self.ret.region to detect ideal
    def ideal(self,image, rect):
        pass

    # decided by your image type: RGB | GREY
    def pre_proc(self, image,type):
        # remove noise or other pro-process
        img = equalization(image,type)
        return img

    def multi_detect(self,image):
        self.pos, threads=[],[]
        [threads.append(threading.Thread(target=self.position, args=(image))) for i in range(NUM_THREADS)]
        for t in threads:
            t.setDaemon(True)
            t.start()
        for t in threads:
            t.join()

    # this function return the target position and self.pos will have n(threads) elements
    def img_pipe(self,image):
        self.log.info("Image has been received in queue.")

        self.log.info("Imgge is been pre-processed.")
        image=self.pre_proc(image,"RGB")

        # use multiple thread to run position to increase accuracy
        self.pos, threads = [], []
        self.ret.reset()
        try:
            self.multi_detect(image=image)
        except:
            self.log.error("Meeting error in multi-thread image algorithm!")
            self.ret.reset()
            return self.ret
        finally:
            self.log.info("Finish feature " + self.name + " detection")

        if len(self.pos) is 0:
            self.ret.exist = False
            self.log.warn("Feature " + self.ret.name + " is not detect!")
            return self.ret

        # calculate variance to ensure accuracy
        centers = [[], []]
        for ele in self.pos:
            centers[0].append((ele[0] + ele[2]) * 0.5)
            centers[1].append((ele[1] + ele[3]) * 0.5)
        wid_std = np.std(centers[0])
        hei_std = np.std(centers[1])
        if (wid_std > WID_ERROR or hei_std > HEI_ERROR):
            self.ret.exist = True
            self.ret.useful = False
            self.log.warning("Feature " + self.ret.name + " has conflicted positions in single detection.")
            return self.ret

        self.ret.region=np.mean(self.pos,0)
        return self.ret

    # this function will decide which direction to go with detected region
    # should return [target_region_position, target_camera_position]
    def translate(self, image, ret, region, camera):
        pass

    # when the position is ideal, we wait for post process
    def postprocess(self, image):
        pass


if __name__ == "__main__":
    pass

