import cv2
import FaceRecognizer

fr = FaceRecognizer.FaceRecognizer(low_res=True)

cap = cv2.VideoCapture(0)

fr.addUser("Yigit", "train_img/yigit2.jpg")
fr.addUser("Pofu", "train_img/pofu.jpg")

while True:
    image = cap.read()[1]
    image = fr.eventLoop(image)
    cv2.imshow("Test", image)
    
    if fr.activeUser != None:
        print(fr.activeUser.name)
    
    if cv2.waitKey(1) & 0xFF == ord('q') or cv2.getWindowProperty("Test", cv2.WND_PROP_VISIBLE) == False:
        cap.release()
        break