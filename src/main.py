''' Module imports '''
import Capture
from Capture import CaptureSource
import cv2
import FaceRecognizer
import GestureRecognizer
import TouchMenu
import CommManager
import numpy as np
import time
import multiprocessing
import FaceMesh


''' Multi-Process Module Instances '''
fr = FaceRecognizer.FaceRecognizer()
fr.addUser("Yigit", "train_img/yigit.jpg")
fr.addUser("Yigit", "train_img/yigit-gozluklu.jpg")
fr.addUser("Pofuduk", "train_img/ahmet.jpg")
fr.addUser("Prronto", "train_img/pronto.jpg")

cm = CommManager.CommManager()

fm = FaceMesh.FaceMesh(angle_coefficient=1)


''' Face Recognition Process Worker '''
def fr_worker(image_queue, result_queue, authenticated_event):
    global fr
    while True:
        if not authenticated_event.is_set():
            try:
                if not image_queue.empty():
                    image = image_queue.get(timeout=0.5)
                    fr.process(image)
                    result_queue.put(fr.getUser())

            except Exception as e:
                print("fr worker exception: ", e)
                continue


''' Communication Manager Process Worker '''
def cm_worker(pitch_yaw_queue, obstacle_detected_event, control_wheelchair_event):
    global cm
    cm.start()
    while True:
        if control_wheelchair_event.is_set():
            try:
                if not pitch_yaw_queue.empty():
                    pitch, yaw = pitch_yaw_queue.get(timeout=0.5)
                obstacleDetected = cm.eventLoop(pitch, yaw)
                if obstacleDetected and not obstacle_detected_event.is_set():
                    obstacle_detected_event.set()
                elif not obstacleDetected and obstacle_detected_event.is_set():
                    obstacle_detected_event.clear()
            except Exception as e:
                print("cm worker exception: ", e)
                continue


''' Face Mesh Process Worker '''
def fm_worker(image_queue, face_detected_event, authenticated_event):
    global fm
    face_detected_event.set()
    while True:
        if authenticated_event.is_set():
            try:
                if not image_queue.empty():
                    image = image_queue.get(timeout=0.5)
                    try:
                        fm.eventLoop(image)
                    except:
                        continue
                    if fm.face == []:
                        face_detected_event.clear()
                    else:
                        face_detected_event.set()

            except Exception as e:
                print("fm worker exception: ", e)
                continue


''' Main Process '''
if __name__ == "__main__":
    manager = multiprocessing.Manager()

    ''' Display Window Creation '''
    cv2.namedWindow("Wheelchair")
    cv2.resizeWindow("Wheelchair", 750, 400)
    cv2.moveWindow("Wheelchair", 25, 25)

    ''' Global variables '''
    run = True
    image = None
    controlWheelchair = False
    wcControlLastToggled = 0
    authenticated = False
    activeUser = ""
    lastActiveUser = None
    calibrating = False

    ''' Function definitions '''
    def stop():
        global run
        run = False
        fr_process.terminate()
        cm_process.terminate()
        fm_process.terminate()
        print("Exit")

    def toggleWheelchairControl():
        global controlWheelchair, wcControlLastToggled
        if (time.time() - wcControlLastToggled > 1.5):
            wcControlLastToggled = time.time()
            controlWheelchair = not controlWheelchair

    def toggleCalibrate():
        global authenticated, calibrating

        if calibrating:
            calibrating = False
            return

        if authenticated and not calibrating:
            calibrating = True
            fm.calibrated = False
            gr.browThresholdCalibrated = False
            fm.calibrationEntryTime = -1
            gr.browCalibrationEntryTime = -1

    def calibrate():
        global calibrating, authenticated, image

        if (not authenticated):
            calibrating = False
            return

        if (not fm.calibrated):
            image = fm.calibrate(image)

        elif (not gr.browThresholdCalibrated):
            image = gr.calibrate(image)

        else:
            cv2.putText(image, "Calibrating...", (400, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            cv2.putText(image, "Calibration Complete", (50, 100),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (40, 200, 13), 2)

            calibrating = False

    ''' Module instances '''
    cap = Capture.Capture(CaptureSource.CV2)
    gr = GestureRecognizer.GestureRecognizer(print=False)
    tm = TouchMenu.TouchMenu()

    ''' Module configurations & initializations '''
    tm.buttonHeight = 100
    tm.imageSize = (600, 400)
    tm.addButton("Calibrate", onClick=toggleCalibrate)
    tm.addButton("Settings", colorR=(0, 0, 255), onClick=tm.settings)
    tm.addButton("  Exit", colorR=(255, 0, 0), onClick=stop)
    tm.start()
    cv2.setMouseCallback("Wheelchair", tm.clickEvent)

    ''' Process, Queue, and Event Creation '''
    image_queue = manager.Queue(maxsize=1)
    fr_result_queue = manager.Queue(maxsize=1)
    authenticated_event = manager.Event()

    fr_process = multiprocessing.Process(
        target=fr_worker, args=(image_queue, fr_result_queue, authenticated_event))
    fr_process.start()

    pitch_yaw_queue = manager.Queue(maxsize=2)
    obstacle_detected_event = manager.Event()
    control_wheelchair_event = manager.Event()

    cm_process = multiprocessing.Process(target=cm_worker, args=(
        pitch_yaw_queue, obstacle_detected_event, control_wheelchair_event))
    cm_process.start()

    fm_face_detected_event = manager.Event()
    fm_process = multiprocessing.Process(target=fm_worker, args=(
        image_queue, fm_face_detected_event, authenticated_event))
    fm_process.start()

    ''' Main Loop '''
    while run:
        image = cap.getFrame()
        image = cv2.resize(image, (600, 400))

        if image_queue.full():
            image_queue.get()   # remove oldest image from queue if full
        image_queue.put(image)

        authenticated_event.set() if authenticated else authenticated_event.clear()
        control_wheelchair_event.set() if controlWheelchair else control_wheelchair_event.clear()

        if (not authenticated):
            cv2.putText(image, "Facial Recognition in Progress", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
            cv2.putText(image, "Please Look at the Camera", (90, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 50, 255), 2)

            if not fr_result_queue.empty():
                tUser = fr_result_queue.get()
                if tUser is not None:
                    print(f"User Recognized: {tUser.name}")
                    activeUser = tUser.name
                    authenticated = True

            if (not fm.calibrated or not gr.browThresholdCalibrated):
                calibrating = False
                toggleCalibrate()
        else:

            if not fm_face_detected_event.is_set():
                authenticated = False
                calibrating = False
                activeUser = ""
                fr_result_queue.get()
                while image_queue.qsize() > 0:
                    image_queue.get()
                controlWheelchair = False
                continue

            if (lastActiveUser != activeUser):
                lastActiveUser = activeUser
                if (not calibrating):
                    toggleCalibrate()

            yaw, pitch = fm.getYawPitch()
            if pitch_yaw_queue.full():  # Remove oldest data from queue if full
                pitch_yaw_queue.get()
            pitch_yaw_queue.put((pitch, yaw))
            gr.process(fm.face, pitch, yaw, fm.pitchOffset, fm.yawOffset)

            if (gr.getGesture() == GestureRecognizer.Gesture.BROW_RAISE) and not calibrating:
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
                controlWheelchair = False
                calibrate()

        touchmenuImg = tm.getMenuImg()
        image = np.hstack((image, touchmenuImg))
        cv2.imshow("Wheelchair", image)

        if (not run or cv2.getWindowProperty("Wheelchair", cv2.WND_PROP_VISIBLE) == False):
            fr_process.terminate()
            cm_process.terminate()
            fm_process.terminate()
            break
        if cv2.waitKey(1) & 0xFF == ord('q') or cv2.waitKey(1) & 0xFF == ord('Q') or cv2.waitKey(1) & 0xFF == 27:  # ESC or q to exit
            fr_process.terminate()
            cm_process.terminate()
            fm_process.terminate()
            break

    fr_process.join()
    cm_process.join()
    cv2.destroyAllWindows()
    exit()
