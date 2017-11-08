import logging
import time
import os
from parameters import *
# pay attention: the ending of the input for log should not be \n.
class log:
    def __init__(self,loginfo=None):
        self.loginfo=loginfo
        logging.basicConfig(level=logging.ERROR,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename='log_record',
                            filemode='w')

    def info(self,string):
        time.sleep(0.5)
        os.chdir(cwd)
        logging.info(string)
        while len(string)>DEFAULT_LENGTH:
            s=string[0:DEFAULT_LENGTH]
            self.loginfo.insertLogInfo(s + '\n')
            string=string[DEFAULT_LENGTH:]
        self.loginfo.insertLogInfo(string+'\n')

    def warn(self,string):
        time.sleep(0.2)
        os.chdir(cwd)
        logging.warning(string)
        while len(string)>DEFAULT_LENGTH:
            s=string[0:DEFAULT_LENGTH]
            self.loginfo.insertLogInfo(s + '\n')
            string=string[DEFAULT_LENGTH:]
        self.loginfo.insertLogInfo(string+'\n')

    def error(self,string):
        time.sleep(0.2)
        os.chdir(cwd)
        logging.error(string)
        while len(string)>DEFAULT_LENGTH:
            s=string[0:DEFAULT_LENGTH]
            self.loginfo.insertLogInfo(s + '\n')
            string=string[DEFAULT_LENGTH:]
        self.loginfo.insertLogInfo(string+'\n')