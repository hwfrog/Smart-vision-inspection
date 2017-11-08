from Feature import *
import threading
import Region
import Camera
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
class my_feature_name(feature):
    def __init__(self,name='Default name',num_threads=3,log=None):
        self.ret.name=name
        self.num_threads=2
        self.log=log
        feature.__init__(num_threads, Region([0.0,0.0,0.0],1.0), Camera([0.0,0.0]), name)
        # define your variables
        pass

    def position(self, image, arg0=None, arg1=None, arg2=None):
        # define your method
        # judge whether the feature exist
        if self.ret.exist is False:
            self.pos.append([None,None,None,None])
        # return the target position

    # return True or False
    def ideal(self, image):
        # define your method
        pass

    # This return a array [[0,0,0],[0,0]] -> The updated region position and updated camera angle
    def translate(self, returnInfo):
        # define your method
        pass

    def multi_detect(self,image):
        self.pos, threads=[],[]
        [threads.append(threading.Thread(target=self.position, args=(image))) for i in range(NUM_THREADS)]
        for t in threads:
            t.setDaemon(True)
            t.start()
        for t in threads:
            t.join()

