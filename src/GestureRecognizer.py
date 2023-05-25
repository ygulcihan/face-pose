import numpy as np
import landmark_indexes
import time
from enum import Enum


class Gesture(Enum):
    BROW_RAISE = 1
    BLINK = 2

class GestureRecognizer:
    __print__ = False
    __brow_raise_threshold__ = 590
    __normalized_ratio__ = 0
    __ratioList__ = []
    __weightList__ = []
    __avgRatio__ = 0

    def __init__(self, print=False):
        self.__print__ = print
        
    def setBrowRaiseThreshold(self, threshold):
        self.__brow_raise_threshold__ = threshold

    def process(self, face, pitch, yaw):
        self.__checkBlink(face, pitch, yaw)
        self.__checkEyebrowRaise(face, pitch, yaw)    

    def __checkBlink(self, face, pitch, yaw):
        return

    def __checkEyebrowRaise(self, face, pitch, yaw):
        
        if face == []:
            return

        head_height = self.__findDistance(
            face[landmark_indexes.MID_FACE_DOWN], face[landmark_indexes.MID_FACE_UP])

        if yaw < 0:
            brow_to_head_distance = self.__findDistance(
                face[landmark_indexes.LEFT_BROW_UP], face[landmark_indexes.LEFT_FACE_UP])

        else:
            brow_to_head_distance = self.__findDistance(
                face[landmark_indexes.RIGHT_BROW_UP], face[landmark_indexes.RIGHT_FACE_UP])

        distRatio = head_height / brow_to_head_distance * 100

        if pitch > 0:
            correctedRatio = distRatio - (pitch * 8) + (yaw * 1.5)
        else:
            correctedRatio = distRatio - (pitch * 3.5) + (yaw / 12)

        self.__ratioList__.append(correctedRatio)

        if len(self.__ratioList__) >= 10:
            self.avgRatio = np.average(
                self.__ratioList__)

            weight = 1 / (1 - (abs(self.avgRatio -
                                   correctedRatio) / self.avgRatio))

            self.__weightList__.append(weight)

            if len(self.__weightList__) >= 10:
                self.__normalized_ratio__ = np.average(
                    self.__ratioList__, weights=self.__weightList__)
                self.__weightList__.pop(0)

            else:
                self.__normalized_ratio__ = np.average(
                    self.__ratioList__)

            self.__ratioList__.pop(0)

        else:
            self.__normalized_ratio__ = correctedRatio

        if (self.__normalized_ratio__ > self.__brow_raise_threshold__):
            self.brow_raised = True
        else:
            self.brow_raised = False

        if self.__print__:
            print(f"Ratio: {int(distRatio)} | Corrected: {int(correctedRatio)} | Normalized: {int(self.__normalized_ratio__)} | Threshold: {self.__brow_raise_threshold__} | Raised: {self.brow_raised}")

    def __findDistance(self, p1, p2):
        x_distance = p2[0] - p1[0]
        y_distance = p2[1] - p1[1]
        return np.sqrt(x_distance**2 + y_distance**2)

    def getGesture(self):
        if self.brow_raised:
            return Gesture.BROW_RAISE
        else:
            return None
