''' Module imports '''
import Capture
from Capture import CaptureSource
import cv2
from GestureRecognizer import Gesture
import TouchMenu
import numpy as np
import time
import multiprocessing

''' Face Recognition Process Worker '''
def fr_worker(image_to_process, active_user, authenticated_event):
    import FaceRecognizer
    fr = FaceRecognizer.FaceRecognizer()
    fr.addUser("Yigit", "train_img/yigit.jpg")
    fr.addUser("Yigit", "train_img/yigit-gozluklu.jpg")
    fr.low_res = True
    while True:
        if not authenticated_event.is_set():
            try:
                image = image_to_process.get()
                if image is None:
                    continue
                fr.process(image)
                image_to_process.set(None)

                if fr.getUser() is not None:
                    print(f"User Recognized: {fr.getUser().name}")
                    active_user.set(fr.getUser().name)
                    authenticated_event.set()

            except Exception as e:
                print("fr worker exception: ", e)
                continue


''' Face Mesh Process Worker '''
def fm_worker(image_to_process, authenticated_event, pitch_yaw, control_wheelchair_event, calibrating_event, calibration_instruction):
    import FaceMesh
    import GestureRecognizer
    fm = FaceMesh.FaceMesh()
    gr = GestureRecognizer.GestureRecognizer()
    gr.print = False
    brow_raise_time = None
    while True:
        if authenticated_event.is_set():
            try:
                image = image_to_process.get()
                if image is None:
                    continue
                image_to_process.set(None)

                try:
                    if calibrating_event.is_set():
                        fm.calibrated = False
                        gr.browThresholdCalibrated = False
                        fm.calibrationEntryTime = -1
                        gr.browCalibrationEntryTime = -1
                        
                        while calibrating_event.is_set():
                            image = image_to_process.get()
                            if image is None:
                                continue
                            image_to_process.set(None)
                            fm.process(image)
                            if not fm.calibrated:
                                instruction = fm.calibrate(image) #instructions
                                calibration_instruction.set(instruction)
                            elif not gr.browThresholdCalibrated:
                                gr.process(fm.face, fm.pitch, fm.yaw, fm.pitchOffset, fm.yawOffset)
                                instruction = gr.calibrate() #instructions
                                calibration_instruction.set(instruction)
                            else:
                                calibration_instruction.set("   Calibration Complete")
                                time.sleep(1)
                                calibrating_event.clear()                            
                    else:    
                        fm.process(image)

                        if fm.face == []:
                            authenticated_event.clear()
                            calibrating_event.clear()
                            # activeUser = ""
                            control_wheelchair_event.clear()
                            continue

                        pitch_yaw.set((fm.pitch, fm.yaw))

                        gr.process(fm.face, fm.pitch, fm.yaw,
                                fm.pitchOffset, fm.yawOffset)
                        
                        if gr.getGesture() == Gesture.BROW_RAISE:
                            if brow_raise_time is None:
                                brow_raise_time = time.time()
                                
                            if time.time() - brow_raise_time > 2:  
                                
                                if not control_wheelchair_event.is_set():
                                    control_wheelchair_event.set()
                                else:
                                    control_wheelchair_event.clear()
                                    
                                brow_raise_time = None
                except Exception as e:
                    print("fm calibration exception: ", e)
                    

            except Exception as e:
                print("fm worker exception: ", e)
                continue


''' Communication Manager Process Worker '''
def cm_worker(pitch_yaw, obstacle_detected_event, control_wheelchair_event):
    import CommManager
    cm = CommManager.CommManager()
    cm.start()
    while True:
        if control_wheelchair_event.is_set():
            try:
                pitch, yaw = pitch_yaw.get()
                obstacleDetected = cm.eventLoop(pitch, yaw)
                if obstacleDetected and not obstacle_detected_event.is_set():
                    obstacle_detected_event.set()
                elif not obstacleDetected and obstacle_detected_event.is_set():
                    obstacle_detected_event.clear()
            except Exception as e:
                print("cm worker exception: ", e)
                continue


''' Main Process '''
if __name__ == "__main__":
    manager = multiprocessing.Manager()

    ''' Module instances '''
    cap = Capture.Capture(CaptureSource.CV2)
    tm = TouchMenu.TouchMenu()

    ''' Display Window Creation '''
    cv2.namedWindow("Wheelchair")
    cv2.resizeWindow("Wheelchair", 750, 400)
    cv2.moveWindow("Wheelchair", 25, 25)

    ''' Global variables '''
    run = True
    image = None
    wcControlLastToggled = 0
    lastActiveUser = None

    ''' Process, Queue, and Event Creation '''
    # image_queue = manager.Queue(maxsize=10)
    image_to_process = manager.Value(np.ndarray, None)
    pitch_yaw = manager.Value(tuple, (0, 0))
    active_user = manager.Value(str, "")
    calibration_instruction = manager.Value(str, "")
    
    class DebugVars:
        def __init__(self):
            self.image_to_process = None
            self.pitch_yaw = None
            self.active_user = None
            self.calibration_instruction = None
    
    debug = DebugVars()

    authenticated_event = manager.Event()
    calibrating_event = manager.Event()
    obstacle_detected_event = manager.Event()
    control_wheelchair_event = manager.Event()

    fr_process = multiprocessing.Process(
        target=fr_worker, name="fr_process", args=(image_to_process, active_user, authenticated_event))

    fm_process = multiprocessing.Process(
        target=fm_worker, name="fm_process", args=(image_to_process, authenticated_event, pitch_yaw, control_wheelchair_event, calibrating_event, calibration_instruction))

    cm_process = multiprocessing.Process(
        target=cm_worker, name="cm_process", args=(pitch_yaw, obstacle_detected_event, control_wheelchair_event))

    ''' Function definitions '''
    def stop():
        global run
        run = False
        fr_process.terminate()
        cm_process.terminate()
        fm_process.terminate()
        print("Exit")

    def toggleCalibrate():
        global authenticated_event, calibrating_event

        if calibrating_event.is_set():
            calibrating_event.clear()

        elif authenticated_event.is_set():
            calibrating_event.set()

    ''' Module configurations & initializations '''
    cv2.setMouseCallback("Wheelchair", tm.clickEvent)

    tm.buttonHeight = 100
    tm.imageSize = (600, 400)
    tm.addButton("Calibrate", onClick=toggleCalibrate)
    tm.addButton("Settings", colorR=(0, 0, 255), onClick=tm.settings)
    tm.addButton("  Exit", colorR=(255, 0, 0), onClick=stop)
    tm.start()

    fr_process.start()
    cm_process.start()
    fm_process.start()

    ''' Main Loop '''
    while run:
        
        debug.image_to_process = image_to_process.get()
        debug.pitch_yaw = pitch_yaw.get()
        debug.active_user = active_user.get()
        debug.calibration_instruction = calibration_instruction.get()
        
        image = cap.getFrame()
        image = cv2.resize(image, (600, 400))
        
        if image_to_process.get() is None:
            image_to_process.set(image)

        '''
        if image_queue.full():
            image_queue.get()   # remove oldest image from queue if full
        image_queue.put(image)
        '''

        if (not authenticated_event.is_set()):
            cv2.putText(image, "Facial Recognition in Progress", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
            cv2.putText(image, "Please Look at the Camera", (90, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 50, 255), 2)
                
        else:
            if (lastActiveUser != active_user.get()):
                lastActiveUser = active_user.get()
                if (not calibrating_event.is_set()):
                    toggleCalibrate()

            pitch, yaw = pitch_yaw.get()

            cv2.putText(image, f"User: {active_user.get()}", (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.8, (40, 200, 13), 3)
            cv2.putText(image, "Control: Enabled" if control_wheelchair_event.is_set() else "Control: Disabled", (20, 370),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (40, 200, 13) if control_wheelchair_event.is_set() else (50, 50, 255), 2)

            if not calibrating_event.is_set():
                cv2.putText(image, "Pitch: " + str(int(pitch)), (420, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                cv2.putText(image, "Yaw:  " + str(int(yaw)), (420, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        
        if calibrating_event.is_set():
            cv2.putText(image, "Calibrating...", (400, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.putText(
                image, calibration_instruction.get(), (50, 100), cv2.FONT_HERSHEY_COMPLEX, 1,
                    (0, 0, 255) if calibration_instruction.get() != "   Calibration Complete" else (40, 200, 13), 2)
            
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
    fm_process.join()
    cv2.destroyAllWindows()
    exit()
