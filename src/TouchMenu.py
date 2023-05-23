import cv2
import numpy as np


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
    imageSize = (0, 0)
    buttonHeight = 100
    menuImg = cv2.resize(cv2.imread("src/black_bg.jpg"), size)
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


""" tm = TouchMenu()
tm.buttonHeight = 100
tm.addButton("Calibrate", onClick=tm.calibrate)
tm.addButton("Settings", colorR=(0, 0, 255), onClick=tm.settings)
tm.addButton("  Exit", colorR=(255, 0, 0), onClick=cv2.destroyAllWindows)
tm.start()

cv2.namedWindow("Touch Menu", cv2.WINDOW_NORMAL)
cv2.setMouseCallback("Touch Menu", tm.clickEvent)

while True:
    cv2.imshow("Touch Menu", tm.getMenuImg())
    if cv2.waitKey(1) & 0xFF == ord('q') or cv2.getWindowProperty("Touch Menu", cv2.WND_PROP_VISIBLE) < 1:
        break
 """