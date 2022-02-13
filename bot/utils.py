from time import sleep
import cv2
import pytesseract
import numpy as np
import json
import pyautogui
import re

def extractDate(s):
    count=0
    retSize=0
    prefix=""
    for c in s:
        if c==':':
            count+=1
        if count==4:
            break
        prefix +=c
        retSize+=1
    if retSize<20:
        return prefix
    else:
        return s[:19]

def sanitizeString(s):
    ret = "Day " + s
    return ret.replace('\n', "").replace('/', "").replace('|', "").replace('=', "").replace('>', "").replace('—', "").replace('.', "").replace('-', "").replace('(', "").replace(')', "").replace('{', "").replace('}', "").replace('[', "").replace(']', "").replace('®', "").replace('‘', "").replace("'", "").replace('!', "").replace('§', "").replace(',', ":").replace('.', ":").replace(';', ":")

def visualize(img):
    cv2.imshow("visualize", img)
    cv2.waitKey(0) 
    cv2.destroyAllWindows() 

def preprocessing(img):
    return img * (np.sum(img, axis=2)>230)[:,:,np.newaxis]