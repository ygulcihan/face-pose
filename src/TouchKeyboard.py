import cv2
from time import sleep
import numpy as np

class Button():
    def __init__(self, pos, text, size=[70, 70]):
        self.pos = pos
        self.size = size
        self.text = text

class TouchKeyboard:

    buttonList = []
    hOffset = 20
    vOffset = 20

    keys = [
        ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
        ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]
        ]

    def __init__(self):
        for i in range(len(self.keys)):
            for j, key in enumerate(self.keys[i]):
                self.buttonList.append(Button([80 * j + self.hOffset, 80 * i + self.vOffset], key))

    def cornerRect(img, bbox, l=30, t=5, rt=1,
               colorR=(255, 0, 255), colorC=(0, 255, 0)):
        """
        :param img: Image to draw on.
        :param bbox: Bounding box [x, y, w, h]
        :param l: length of the corner line
        :param t: thickness of the corner line
        :param rt: thickness of the rectangle
        :param colorR: Color of the Rectangle
        :param colorC: Color of the Corners
        :return:
        """
        x, y, w, h = bbox
        x1, y1 = x + w, y + h
        if rt != 0:
            cv2.rectangle(img, bbox, colorR, rt)
        # Top Left  x,y
        cv2.line(img, (x, y), (x + l, y), colorC, t)
        cv2.line(img, (x, y), (x, y + l), colorC, t)
        # Top Right  x1,y
        cv2.line(img, (x1, y), (x1 - l, y), colorC, t)
        cv2.line(img, (x1, y), (x1, y + l), colorC, t)
        # Bottom Left  x,y1
        cv2.line(img, (x, y1), (x + l, y1), colorC, t)
        cv2.line(img, (x, y1), (x, y1 - l), colorC, t)
        # Bottom Right  x1,y1
        cv2.line(img, (x1, y1), (x1 - l, y1), colorC, t)
        cv2.line(img, (x1, y1), (x1, y1 - l), colorC, t)

        return img

    def drawAll(self, img):
        for button in self.buttonList:
            x, y = button.pos
            w, h = button.size
            self.cornerRect(img, (button.pos[0], button.pos[1], button.size[0], button.size[1]), l=20, rt=5, t=1)
            cv2.rectangle(img, button.pos, (x + w, y + h), (0, 0, 0), cv2.FILLED)
            cv2.putText(img, button.text, (x + 20, y + 45),
                        cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 4)
            
        return img
    
if __name__ == "__main__":
    import numpy as np
    tk = TouchKeyboard()
    img = np.zeros((350, 830))
    img = tk.drawAll(img)
    cv2.imshow("Touch Keyboard", img)
    cv2.waitKey(0)
    