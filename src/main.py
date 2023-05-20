import Capture
from Capture import CaptureSource
import cv2
import FaceRecognizer
import FaceMesh
import GestureRecognizer
import TouchMenu
import numpy as np

cap = Capture.Capture(CaptureSource.CV2)
fr = FaceRecognizer.FaceRecognizer()
fm = FaceMesh.FaceMesh(angle_coefficient=1)

gr = GestureRecognizer.GestureRecognizer(print=False)
fr.addUser("Yigit", "train_img/yigit.jpg")
fr.addUser("Pofuduk", "train_img/ahmet.jpg")

tm = TouchMenu.TouchMenu()
tm.buttonHeight = 100
tm.imageSize = (600, 400)
tm.addButton("Calibrate", onClick=tm.calibrate)
tm.addButton("Settings", colorR=(0, 0, 255), onClick=tm.settings)
tm.addButton("  Exit", colorR=(255, 0, 0), onClick=cv2.destroyAllWindows)
tm.start()

cv2.namedWindow("Wheelchair")
cv2.setMouseCallback("Wheelchair", tm.clickEvent)

authenticated = False
activeUser = ""

addText = True

while True:
    image = cap.getFrame()
    image = cv2.resize(image, (600, 400))

    if (not authenticated):
        image = fr.eventLoop(image)
        if (fr.getUser() != None):
            print(f"User Recognized: {fr.getUser().name}")
            activeUser = fr.getUser().name
            authenticated = True
        if addText:
            cv2.putText(image, "Not Authenticated", (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
    else:
        fm.eventLoop(image)

        if fm.face == []:
            authenticated = False
            activeUser = ""
            continue

        yaw, pitch = fm.getYawPitch()
        gr.process(fm.face, pitch, yaw)

        '''
        if gr.getGesture() != None:
            print(gr.getGesture())
        '''
        if addText:
            # Add the text on the image
            cv2.putText(image, f"User: {activeUser}", (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (100, 255, 100), 2)
            cv2.putText(image, "Pitch: " + str(int(pitch)), (450, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.putText(image, "Yaw: " + str(int(yaw)), (450, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    touchmenuImg = tm.getMenuImg()
    image = np.hstack((image, touchmenuImg))

    cv2.imshow("Wheelchair", image)
    if (cv2.waitKey(1) & 0xFF == ord('q') or cv2.getWindowProperty("Wheelchair", cv2.WND_PROP_VISIBLE) == False):
        break
