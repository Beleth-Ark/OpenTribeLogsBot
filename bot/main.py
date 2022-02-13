from time import sleep
import cv2
import pytesseract
import numpy as np
import json
import pyautogui
import keyboard
import re
from utils import *

config_fd = open('config.json')
config = json.load(config_fd)

pytesseract.pytesseract.tesseract_cmd = config['tesseractLocation']

class screenManager:
    def __init__(self) -> None:
        pass

    def getScreenshot(self):
        screen = np.array(pyautogui.screenshot())
        return screen

    def getGrayScreenshot(self):
        grayFrame = cv2.cvtColor(self.getScreenshot(), cv2.COLOR_BGR2GRAY)
        return grayFrame

class arkStateManager:
    def __init__(self, config) -> None:
        self.config=config

    def logsAreOpened(self, screenManager):
        logsTemplate = cv2.imread("templates/logs.png", cv2.IMREAD_GRAYSCALE)
        logsTemplate = cv2.Canny(logsTemplate, threshold1=5000, threshold2=2000, apertureSize=5) 

        img = screenManager.getGrayScreenshot()[self.config['screen']['topLeftCornerLogsIconX']:self.config['screen']['bottomRightCornerLogsIconX'],self.config['screen']['topLeftCornerLogsIconY']:self.config['screen']['bottomRightCornerLogsIconY']]
        img = cv2.Canny(img, threshold1=5000, threshold2=2000, apertureSize=5)

        res = cv2.matchTemplate(img, logsTemplate, cv2.TM_CCOEFF)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        return (max_val > 50000000)

class logsUpdater:
    def __init__(self, config):
        self.memory=[]
        self.maxMemorySize=100
        self.initialized=False
        self.lastScreenshot=None
        self.logs=[]
        self.config=config

    def getNewEvents(self, screen):
        ret = []

        currentScreenshot = screen.getScreenshot()

        if (not self.initialized) or (np.mean(np.mean(np.abs(currentScreenshot[:, :, 0]-self.lastScreenshot[:, :, 0]),axis=0),axis=0)>70):
            rawInput = [sanitizeString(s) for s in re.split("Day|Dav|Dau", pytesseract.image_to_string(preprocessing(currentScreenshot[self.config['screen']['topLeftCornerLogsX']:self.config['screen']['bottomRightCornerLogsX'],self.config['screen']['topLeftCornerLogsY']:self.config['screen']['bottomRightCornerLogsY']]), config='--psm 6'))[1:]]
            rawInput.reverse()

            if rawInput != None:
                for input in rawInput:
                    date = extractDate(input)
                    if date not in self.memory:
                        self.memory.append(date)
                        if self.initialized:
                            ret.append(input)
                        if len(self.memory)>self.maxMemorySize:
                            self.memory.pop(0)

        self.lastScreenshot = currentScreenshot
        self.initialized=True
        self.logs += ret
        return ret 

class discordIntegrator:
    def __init__(self, config) -> None:
        self.config = config
        self.container = config["discordContainer"]
        self.discordShortcut = config["discordShortcut"]

    def openCloseDiscord(self):
        pyautogui.press(self.discordShortcut)
        sleep(2)

    def writeInput(self, s):
        s = self.container+s+self.container
        for k, v in self.config["alerts"].items():
            if k in s:
                s+=v 
        keyboard.write(s, 0.02)
        sleep(0.1)
        pyautogui.press('enter')
        sleep(0.1)

    def writeInputList(self, l):
        self.openCloseDiscord()
        for s in l:
            self.writeInput(s)
        self.openCloseDiscord()

screen = screenManager()
updater = logsUpdater(config)
states = arkStateManager(config)
discord = discordIntegrator(config)

print("The bot is running! Switch to ARK Survival Evolved and open your tribe logs.")
while True:
    if states.logsAreOpened(screen):
        news = updater.getNewEvents(screen)
        if len(news)>0:
            discord.writeInputList(news)
    sleep(1)