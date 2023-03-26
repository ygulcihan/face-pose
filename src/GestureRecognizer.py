import numpy as np
import landmark_indexes
import time


def process(face, pitch, yaw):

    __checkBlink(face, pitch, yaw)
    __checkEyebrowRaise(face, pitch, yaw)


def __checkBlink(face, pitch, yaw):
    return


def __checkEyebrowRaise(face, pitch, yaw):  # TODO: Add ratioing with pitch and yaw

    brow_raise_threshold = 590

    head_height = __findDistance(
        face[landmark_indexes.MID_FACE_DOWN], face[landmark_indexes.MID_FACE_UP])

    if yaw < 0:
        brow_to_head_distance = __findDistance(
            face[landmark_indexes.LEFT_BROW_UP], face[landmark_indexes.LEFT_FACE_UP])

    else:
        brow_to_head_distance = __findDistance(
            face[landmark_indexes.RIGHT_BROW_UP], face[landmark_indexes.RIGHT_FACE_UP])

    if not hasattr(__checkEyebrowRaise, "ratioList"):
        __checkEyebrowRaise.ratioList = []

    if not hasattr(__checkEyebrowRaise, "weightList"):
        __checkEyebrowRaise.weightList = []

    distRatio = head_height / brow_to_head_distance * 100
    
    if pitch > 0:
        correctedRatio = distRatio - (pitch * 8) + (yaw * 1.5)
    else:
        correctedRatio = distRatio - (pitch * 3.5) + (yaw / 12)

    __checkEyebrowRaise.ratioList.append(correctedRatio)

    if len(__checkEyebrowRaise.ratioList) >= 10:
        __checkEyebrowRaise.avgRatio = np.average(
            __checkEyebrowRaise.ratioList)

        weight = 1 / (1 - (abs(__checkEyebrowRaise.avgRatio -
                               correctedRatio) / __checkEyebrowRaise.avgRatio))

        __checkEyebrowRaise.weightList.append(weight)

        if len(__checkEyebrowRaise.weightList) >= 10:
            normalizedRatio = np.average(
                __checkEyebrowRaise.ratioList, weights=__checkEyebrowRaise.weightList)
            __checkEyebrowRaise.weightList.pop(0)

        else:
            normalizedRatio = np.average(__checkEyebrowRaise.ratioList)

        __checkEyebrowRaise.ratioList.pop(0)

    else:
        normalizedRatio = correctedRatio

    if (normalizedRatio > brow_raise_threshold):
        brow_raised = True
    else:
        brow_raised = False

    print(f"Ratio: {int(distRatio)} | Corrected: {int(correctedRatio)} | Normalized: {int(normalizedRatio)} | Threshold: {brow_raise_threshold} | Raised: {brow_raised}")
    time.sleep(0.1)

def __findDistance(p1, p2):
    x_distance = p2[0] - p1[0]
    y_distance = p2[1] - p1[1]
    return np.sqrt(x_distance**2 + y_distance**2)
