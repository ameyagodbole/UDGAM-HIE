import numpy as np
import cv2
from matplotlib import pyplot as plt
import imutils
import os
import sys

os.system("mkdir cropped_frames")
for i in range(1,10):

spath = "./frames/"+str(i)+".jpg" 
dpath = "./cropped_frames/"+str(i)+".png"
if os.path.exists(spath):
    img = cv2.imread("test5.jpg")
    img = cv2.resize(img, (600,600))
    mask = np.zeros(img.shape[:2],np.uint8)
    print(img.shape) 
    bgdModel = np.zeros((1,65),np.float64)
    fgdModel = np.zeros((1,65),np.float64)

    rect = (10,10,500, 500)
    cv2.grabCut(img,mask,rect,bgdModel,fgdModel,5,cv2.GC_INIT_WITH_RECT)

    mask2 = np.where((mask==2)|(mask==0),0,1).astype('uint8')
    img = img*mask2[:,:,np.newaxis]
    im2 = img.copy()
    im2[:, :, 0] = img[:, :, 2]
    im2[:, :, 2] = img[:, :, 0]
    plt.imsave(dpath,im2)