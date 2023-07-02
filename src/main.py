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


fr = FaceRecognizer.FaceRecognizer()
fr.addUser("Yigit", "train_img/yigit.jpg")
fr.addUser("Yigit", "train_img/yigit-gozluklu.jpg")
fr.addUser("Pofuduk", "train_img/ahmet.jpg")
fr.addUser("Prronto", "train_img/pronto.jpg")


''' Face Recognition Process Worker '''
def fr_worker(image_queue, result_queue):
    global fr
    while True:
        try:
            image = image_queue.get(timeout=0.5)
            fr.process(image)
            result_queue.put(fr.getUser())
            
        except Exception as e:
            print(e)
            continue
        
    
if __name__ == "__main__":
    
    manager = multiprocessing.Manager()
    ''' Import FaceMesh after creating manager to avoid double process creation '''
    import FaceMesh  
    fm = FaceMesh.FaceMesh(angle_coefficient=1)
        
    ''' Display Window Creation '''
    load_screen_bg = cv2.resize(cv2.imread("atilim_logo_bg.jpg"), (750, 400))
    cv2.imshow("Wheelchair", load_screen_bg)
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
    cm = CommManager.CommManager()
    gr = GestureRecognizer.GestureRecognizer(print=False)
    tm = TouchMenu.TouchMenu()
    
    
    ''' Module configurations & initializations '''
    cm.start()
    tm.buttonHeight = 100
    tm.imageSize = (600, 400)
    tm.addButton("Calibrate", onClick=toggleCalibrate)
    tm.addButton("Settings", colorR=(0, 0, 255), onClick=tm.settings)
    tm.addButton("  Exit", colorR=(255, 0, 0), onClick=stop)
    tm.start()
    cv2.setMouseCallback("Wheelchair", tm.clickEvent)

    
    ''' Process, Queue, and Event Creation '''
    image_queue = manager.Queue(maxsize=10)
    fr_result_queue = manager.Queue(maxsize=1)
    
    fr_process = multiprocessing.Process(
        target=fr_worker, args=(image_queue, fr_result_queue))
    fr_process.start()
        
    
    ''' Main Loop '''
    while run:
        image = cap.getFrame()
        image = cv2.resize(image, (600, 400))
        
        if image_queue.full():
            image_queue.get()   # remove oldest image from queue if full
        image_queue.put(image)
        
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
            fm.eventLoop(image)
            
            if fm.face == []:
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
            gr.process(fm.face, pitch, yaw, fm.pitchOffset, fm.yawOffset)
            
            if (gr.getGesture() == GestureRecognizer.Gesture.BROW_RAISE) and not calibrating:
                toggleWheelchairControl()
                
            if controlWheelchair:
                cm.eventLoop(speed=pitch, position=yaw)
                
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
            break
        if cv2.waitKey(1) & 0xFF == ord('q') or cv2.waitKey(1) & 0xFF == ord('Q') or cv2.waitKey(1) & 0xFF == 27:  # ESC or q to exit
            fr_process.terminate()
            break
        
    fr_process.join()
    cv2.destroyAllWindows()
    exit()