import numpy as np
import landmark_indexes


def isEyebrowRaised(face, pitch, yaw): #TODO: Add ratioing with pitch and yaw

    brow_raise_threshold = 16

    brow_to_head_distance = __findDistance(
        face[landmark_indexes.RIGHT_BROW_UP], face[landmark_indexes.RIGHT_FACE_UP])
    head_height = __findDistance(
        face[landmark_indexes.MID_FACE_DOWN], face[landmark_indexes.MID_FACE_UP])

    ratioList = []
    ratio = brow_to_head_distance / head_height * 100
    ratioList.append(ratio)
    if ratioList.__len__() > 6:
        ratioList.pop(0)
    ratioAvg = sum(ratioList) / ratioList.__len__()

    if (ratioAvg < brow_raise_threshold):
        brow_raised = True
    else:
        brow_raised = False

    print(f"Threshold: {brow_raise_threshold} | Distance Ratio: {round(ratioAvg,2)} | Raised: {brow_raised}")


def __findDistance(p1, p2):
    x_distance = p2[0] - p1[0]
    y_distance = p2[1] - p1[1]
    return np.sqrt(x_distance**2 + y_distance**2)
