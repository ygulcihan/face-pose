import cv2
import numpy as np
import TouchKeyboard


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
    menuImg = cv2.resize(cv2.imread("resources/black_bg.jpg"), size)
    buttonCount = 0
    buttons = []
    addUserWindowTitle = "Enter name for new user"
    touchKeyboard = None

    def __init__(self):
        self.touchKeyboard = TouchKeyboard.TouchKeyboard()

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

    def calibrate(self):
        print("Calibrate")

    def settings(self):
        print("Settings")

    def addUserTouchEvent(self, event, x, y, flags, param):
        if x > (800 - 130) and x < 800:  # Check for Cancel Button
            if y > 0 and y < 130:
                if event == cv2.EVENT_LBUTTONDOWN:
                    print("Cancel")
                    cv2.destroyWindow(self.addUserWindowTitle)
        else:
            self.touchKeyboard.clickEvent(event, x, y, flags, param)

    def addUser(self):
        cv2.namedWindow(self.addUserWindowTitle)
        cancelButton = cv2.circle(
            np.zeros((130, 130, 3)), (65, 65), 60, (0, 0, 255), cv2.FILLED)
        cancelButton = cv2.polylines(cancelButton, [np.array(
            [[40, 40], [90, 90]]).astype(int)], True, (255, 255, 255), 10)
        cancelButton = cv2.polylines(cancelButton, [np.array(
            [[90, 40], [40, 90]]).astype(int)], True, (255, 255, 255), 10)
        textBoxImg = np.zeros((130, 670, 3))
        textBoxImg = np.hstack((textBoxImg, cancelButton))
        img = np.vstack((textBoxImg, self.touchKeyboard.getKeyboardImage()))
        self.touchKeyboard.touchOffsets = (0, 130)
        cv2.imshow(self.addUserWindowTitle, img)
        cv2.moveWindow(self.addUserWindowTitle, -2, 0)
        cv2.setMouseCallback(self.addUserWindowTitle, self.addUserTouchEvent)


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
