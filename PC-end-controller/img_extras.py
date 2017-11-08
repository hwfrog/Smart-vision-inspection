import cv2
import numpy as np
import matplotlib.pyplot as plt

# average value filter
def filter2D(img, type, size=5):
    dst=[]
    dst_array=[None,None,None]
    kernel = np.ones((size,size),np.float32)/25
    if type=="GREY":
        img1 = np.float32(img)
        dst = cv2.filter2D(img1, -1, kernel)
        dst = np.int32(dst)
    elif type=="RGB":
        assert (False)  # it seems that filter2D cannot be applied to RGB image
        '''
        dst_array[0],dst_array[1],dst_array[2]=cv2.split(img)
        for i in range(3):
            dst_array[i] = cv2.filter2D(np.float32(dst_array[i]), -1, kernel)
        dst=cv2.merge([dst_array[0],dst_array[1],dst_array[2]])
        '''
    return dst

# Gaussian filter
def GaussianBlur(img,type,size=5):
    dst=[]
    dst_array=[None,None,None]
    if type=="GREY":
        img1 = np.float32(img)
        dst = cv2.GaussianBlur(img,(size,size),0)
    elif type=="RGB":
        dst_array[0],dst_array[1],dst_array[2]=cv2.split(img)
        for i in range(3):
            dst_array[i] = cv2.GaussianBlur(dst_array[i],(size,size),0)
        dst=cv2.merge([dst_array[0],dst_array[1],dst_array[2]])
    return dst

# Median value filter
def medianBlur(img,type,size=5):
    dst = []
    dst_array = [None, None, None]
    if type == "GREY":
        img1 = np.float32(img)
        dst = cv2.medianBlur(img,size)
    elif type == "RGB":
        dst_array[0], dst_array[1], dst_array[2] = cv2.split(img)
        for i in range(3):
            dst_array[i] = cv2.medianBlur(dst_array[i],size)
        dst = cv2.merge([dst_array[0],dst_array[1],dst_array[2]])
    return dst

# resize image, size is 2D variable
def resize(img,size):
    dst = cv2.resize(img,size,interpolation=cv2.INTER_CUBIC)
    return dst

# equalize the input image
def equalization(img,type):
    dst = []
    dst_array = [None, None, None]
    if type=="GREY":
        dst=cv2.equalizeHist(img)
    elif type=="RGB":
        dst_array[0],dst_array[1],dst_array[2] = cv2.split(img)
        for i in range(3):
            dst_array[i]=cv2.equalizeHist(dst_array[i])
        dst = cv2.merge([dst_array[0],dst_array[1],dst_array[2]])
    return dst


if __name__=="__main__":
    img=cv2.imread("2.jpg",cv2.IMREAD_COLOR)
    img=resize(img,(400,256))
    dst=filter2D(img,"RGB")
    #cv2.imshow("in",img)
    #cv2.waitKey(0)
    cv2.imshow("out",dst)
    plt.show()
    cv2.waitKey(0)