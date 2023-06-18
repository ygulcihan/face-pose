import Capture
from Capture import CaptureSource
import cv2
import FaceRecognizer
import FaceMesh
import GestureRecognizer
import TouchMenu
import CommManager
import numpy as np
import time
import threading

run = True
controlWheelchair = False
wcControlLastToggled = 0

authenticated = False

activeUser = ""
lastActiveUser = None

calibrating = False
browThresholdCalibrated = False
calibrationEntryTime = 0
calibrationEntryTimeSet = False
calibrationInstruction = "Position your head neutrally"
calibrationInstructionColor = (0, 0, 255)  # BGR

raisedRatio = 0
loweredRatio = 0

frThreadRunning = False


def stop():
    global run
    run = False
    print("Exit")
    
def toggleWheelchairControl():
    global controlWheelchair, wcControlLastToggled
    if (time.time() - wcControlLastToggled > 1.5):
        wcControlLastToggled = time.time()
        controlWheelchair = not controlWheelchair


def toggleCalibrate():
    global authenticated, calibrating, calibrationEntryTimeSet, calibrationInstruction, calibrationInstructionColor

    if calibrating:
        calibrating = False
        return

    if authenticated and not calibrating:
        calibrating = True
        calibrationEntryTimeSet = False
        calibrationInstruction = "Position your head neutrally"
        calibrationInstructionColor = (0, 0, 255)  # BGR


def calibrate():
    global calibrationEntryTime, calibrating, authenticated, calibrationEntryTimeSet, calibrationInstruction, calibrationInstructionColor, browThresholdCalibrated, raisedRatio, loweredRatio

    if (not authenticated):
        calibrating = False
        return

    if (not calibrationEntryTimeSet):
        calibrationEntryTime = time.time()
        calibrationEntryTimeSet = True
        fm.yawOffset = 0
        fm.pitchOffset = 0
        raisedRatio = 0
        loweredRatio = 0
        browThresholdCalibrated = False

    cv2.putText(image, "Calibrating...", (400, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.putText(image, calibrationInstruction, (50, 100),
                cv2.FONT_HERSHEY_COMPLEX, 1, calibrationInstructionColor, 2)

    # Calibrate Pitch and Yaw Offsets
    if (time.time() - calibrationEntryTime >= 5 and time.time() - calibrationEntryTime < 8):  # TODO: Move to FaceMesh.py
        calibrationInstruction = "           Stay still"

    if (time.time() - calibrationEntryTime >= 8 and time.time() - calibrationEntryTime < 13):
        fm.pitchOffset = fm.pitch * -1.0
        fm.yawOffset = fm.yaw * -1.0
        calibrationInstruction = "    Raise your eyebrows"

    # Calibrate Eyebrow Raise Threshold
    if (time.time() - calibrationEntryTime >= 13 and time.time() - calibrationEntryTime < 16):
        if raisedRatio == 0:
            raisedRatio = gr.__normalized_ratio__
        calibrationInstruction = "    Lower your eyebrows"

    if (time.time() - calibrationEntryTime >= 16 and time.time() - calibrationEntryTime < 17):
        if (not browThresholdCalibrated):
            if loweredRatio == 0:
                loweredRatio = gr.__normalized_ratio__

            print("Raised ratio: " + str(raisedRatio))
            print("Lowered ratio: " + str(loweredRatio))
            newThreshold = loweredRatio + ((raisedRatio - loweredRatio) * 70.0 / 100.0)
            print("New threshold: " + str(newThreshold))
            gr.setBrowRaiseThreshold(newThreshold)
            browThresholdCalibrated = True

        calibrationInstructionColor = (40, 200, 13)
        calibrationInstruction = "     Calibration complete"

    if (time.time() - calibrationEntryTime >= 17):
        calibrating = False


cap = Capture.Capture(CaptureSource.IMUTILS)
fr = FaceRecognizer.FaceRecognizer()
fm = FaceMesh.FaceMesh(angle_coefficient=1)

cm  = CommManager.CommManager()

cm.start()

gr = GestureRecognizer.GestureRecognizer(print=False)
fr.addUser("Yigit", "train_img/yigit.jpg")
fr.addUser("Yigit", "train_img/yigit-gozluklu.jpg")
fr.addUser("Pofuduk", "train_img/ahmet.jpg")

tm = TouchMenu.TouchMenu()
tm.buttonHeight = 100
tm.imageSize = (600, 400)
tm.addButton("Calibrate", onClick=toggleCalibrate)
tm.addButton("Settings", colorR=(0, 0, 255), onClick=tm.settings)
tm.addButton("  Exit", colorR=(255, 0, 0), onClick=stop)
tm.start()

cv2.namedWindow("Wheelchair")
cv2.setMouseCallback("Wheelchair", tm.clickEvent)

while run:
    image = cap.getFrame()
    image = cv2.resize(image, (600, 400))

    if (not authenticated):

        if (not frThreadRunning):
            frThread = threading.Thread(target=fr.eventLoop, args=(image,))
            frThread.start()
            frThreadRunning = True

        else:
            frThreadRunning = False

        cv2.putText(image, "Facial Recognition in Progress", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
        cv2.putText(image, "Please Look at the Camera", (90, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 50, 255), 2)
        if (fr.getUser() != None):
            print(f"User Recognized: {fr.getUser().name}")
            activeUser = fr.getUser().name
            authenticated = True

    else:
        threadStarted = False
        fm.eventLoop(image)

        if fm.face == []:
            authenticated = False
            calibrating = False
            activeUser = ""
            controlWheelchair = False
            continue

        if (lastActiveUser != activeUser):
            lastActiveUser = activeUser
            toggleCalibrate()

        yaw, pitch = fm.getYawPitch()
        gr.process(fm.face, pitch, yaw, fm.pitchOffset, fm.yawOffset)
        
        if (gr.getGesture() == GestureRecognizer.Gesture.BROW_RAISE):
            toggleWheelchairControl()
            
        cv2.putText(image, f"User: {activeUser}", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.8, (40, 200, 13), 3)
        cv2.putText(image, "Control: Enabled" if controlWheelchair else "Control: Disabled", (20, 370),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (40, 200, 13) if controlWheelchair else (50, 50, 255), 2)
        if not calibrating:
            cv2.putText(image, "Pitch: " + str(int(pitch)), (420, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.putText(image, "Yaw:  " + str(int(yaw)), (420, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        else:
            calibrate()

    touchmenuImg = tm.getMenuImg()
    image = np.hstack((image, touchmenuImg))

    cv2.imshow("Wheelchair", image)
    if (not run or cv2.getWindowProperty("Wheelchair", cv2.WND_PROP_VISIBLE) == False):
        break
    if cv2.waitKey(1) & 0xFF == ord('q') or cv2.waitKey(1) & 0xFF == ord('Q') or cv2.waitKey(1) & 0xFF == 27:  # ESC or q to exit
        break

cv2.destroyAllWindows()
exit()
