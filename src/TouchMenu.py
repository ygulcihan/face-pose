import cv2
import numpy as np
import TouchKeyboard

touchKeyboard = TouchKeyboard.TouchKeyboard()

class Button:

    id = 0
    text = ""
    yTop = 0
    yBottom = 0
    colorR = (0, 0, 0)
    colorT = (0, 0, 0)
    textOffset = 0
    textOrg = 0
    onClickEvent = None

    def __init__(self, id, text, yTop, yBottom, colorR=(60, 60, 60), colorT=(255, 255, 255), onClick=None):
        self.id = id
        self.text = text
        self.yTop = yTop
        self.yBottom = yBottom
        self.colorR = colorR
        self.colorT = colorT
        self.onClickEvent = onClick
        self.textOffset = 6 if self.id == 0 else 10
        self.textOrg = self.yTop + \
            (self.yBottom - self.yTop) // 2 + self.textOffset

    def draw(self, img, xMax):
        cv2.rectangle(img, (0, self.yTop), (xMax, self.yBottom),
                      self.colorR, cv2.FILLED)
        textOrg = self.yTop + (self.yBottom - self.yTop) // 2 + self.textOffset
        cv2.putText(img, self.text, ((xMax // 2) - 64, textOrg),
                    cv2.FONT_HERSHEY_PLAIN, fontScale=1.75, color=self.colorT, thickness=2)
        return img


class TouchMenu:

    size = (150, 400)
    imageSize = (600, 400)
    buttonHeight = 100
    menuImg = cv2.resize(cv2.imread("black_bg.jpg"), size)
    buttonCount = 0
    buttons = []

    def addButton(self, text, colorR=(60, 60, 60), colorT=(255, 255, 255), onClick=None):
        yTop = self.buttonCount * self.buttonHeight
        self.buttonCount += 1
        yBottom = self.buttonCount * self.buttonHeight
        self.buttons.append(Button(self.buttonCount, text,
                            yTop, yBottom, colorR, colorT, onClick))

    def start(self):
        for button in self.buttons:
            self.menuImg = button.draw(self.menuImg, self.size[0])

    def getMenuImg(self):
        return self.menuImg

    def clickEvent(self, event, x, y, flags, param):
        if (x > self.imageSize[0] and x < self.imageSize[0] + self.size[0]):
            if (event) == cv2.EVENT_LBUTTONDOWN:
                    for button in self.buttons:
                        if (y > button.yTop and y < button.yBottom):
                            button.onClickEvent()

    def eventLoop(self):
        return

    def calibrate(arg):
        print("Calibrate")


    def settings(arg):
        print("Settings")
        
    def addUser(arg):
        windowTitle = "Enter name for new user"
        cv2.namedWindow(windowTitle)
        textBoxImg = np.zeros((130, 800))
        global touchKeyboard
        img = np.vstack((textBoxImg, touchKeyboard.getKeyboardImage()))
        touchKeyboard.touchOffsets = (0, 130)
        cv2.imshow(windowTitle, img)
        cv2.moveWindow(windowTitle, -2, 0)
        cv2.setMouseCallback(windowTitle, touchKeyboard.clickEvent)


if __name__ == "__main__":
    
    run = True
    
    def stop():
        global run
        run = False
        cv2.destroyWindow("Touch Menu")
    
    
    tm = TouchMenu()
    tm.buttonHeight = 100
    tm.imageSize = (0, 0)
    tm.addButton("Add User", colorR=(0, 155, 0), onClick=tm.addUser)
    tm.addButton("Calibrate", onClick=tm.calibrate)
    tm.addButton("Settings", colorR=(255, 140, 0), onClick=tm.settings)
    tm.addButton("  Exit", colorR=(0, 0, 255), onClick=stop)
    tm.start()

    cv2.namedWindow("Touch Menu")
    cv2.setMouseCallback("Touch Menu", tm.clickEvent)

    while run:
        cv2.imshow("Touch Menu", tm.getMenuImg())
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
