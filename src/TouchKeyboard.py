import cv2
from time import sleep
import numpy as np

class Button():
    def __init__(self, pos, text, size=[65, 65]):
        self.pos = pos
        self.size = size
        self.text = text

class TouchKeyboard:

    buttons = []
    inputText = ""
    hOffset = 5
    vOffset = 5
    touchOffsets = [0, 0]

    keys = [
        ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
        ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", "<-"],
        ["Z", "X", "C", "V", "B", "N", "M", ".", "Enter"]
        ]

    def __init__(self):
        for i in range(len(self.keys)):
            for j, key in enumerate(self.keys[i]):
                if i== 3 and j == 8: # Enter Key
                    self.buttons.append(Button([80 * j + self.hOffset, 80 * i + self.vOffset], key, [160, 65]))
                    
                elif i == 2 and j == 9: # Backspace Key
                    self.buttons.append(Button([80 * j + self.hOffset, 80 * i + self.vOffset], key, [85, 65]))
                
                else:
                    self.buttons.append(Button([80 * j + self.hOffset, 80 * i + self.vOffset], key))

    def getKeyboardImage(self, backgroundImage=None):
        
        if backgroundImage is None:
            img = np.zeros((320, 800, 3))
            
        else:
            img = cv2.resize(backgroundImage, (800, 320))
        
        for button in self.buttons:
            x, y = button.pos
            cv2.putText(img, button.text, (x + 20, y + 45),
                        cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 3)
            
        return img
    
    def clickEvent(self, event, x, y, flags, param):        
        correctedX = x - self.touchOffsets[0]
        correctedY = y - self.touchOffsets[1]
        
        for button in self.buttons:
            if (correctedX < button.pos[0] + button.size[0] and correctedX > button.pos[0] and
                correctedY < button.pos[1] + button.size[1] and correctedY > button.pos[1]):
                
                if event == cv2.EVENT_LBUTTONDOWN:
                    if button.text == "<-":
                        self.inputText = self.inputText[:-1]
                    elif button.text == "Enter":
                        self.inputText = ""
                    else:
                        self.inputText += button.text
                    print(self.inputText)
    
    
if __name__ == "__main__":
    import numpy as np
    tk = TouchKeyboard()
    img = np.zeros((320, 800, 3))
    img = tk.getKeyboardImage(img)
    cv2.imshow("Touch Keyboard", img)
    cv2.setMouseCallback("Touch Keyboard", tk.clickEvent)
    cv2.waitKey(0)
    