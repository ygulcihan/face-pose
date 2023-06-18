import cv2
import face_recognition
import User

class FaceRecognizer:

    __low_res = False

    __image_face_locations = []
    __unknown_face_locations = []
    __image_face_encodings = []
    __known_face_encodings = []
    __users = []
    __matches = []
    __activeUserIndex = -1
    __nrOfFramesToSkip = 3
    __skipped_frames = 0

    __activeUser = None

    def __init__(self, low_res=False, number_of_frames_to_skip=7):
        self.__low_res = low_res
        self.__nrOfFramesToSkip = number_of_frames_to_skip

    def addUser(self, name, image_path): #TODO: Save users to file and read them on startup
        newUser = User.User(name, image_path)
        self.__users.append(newUser)
        self.__known_face_encodings.append(newUser.face_encoding)

    def process(self, image):
        
        self.__reset_vars()

        if self.__skipped_frames < self.__nrOfFramesToSkip:
            self.__skipped_frames += 1
            return
        
        self.__skipped_frames = 0
                
        if self.__low_res:
            image = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        image = cv2.cvtColor(src=image, code=cv2.COLOR_BGR2RGB)

        # Find all the faces and face encodings in the current image of video
        self.__image_face_locations = face_recognition.face_locations(
            image, model="hog")
        self.__image_face_encodings = face_recognition.face_encodings(
            image, known_face_locations=self.__image_face_locations, model="small")


        for i, encoding in enumerate(self.__image_face_encodings):
            self.__matches += face_recognition.compare_faces(
                self.__known_face_encodings, encoding, 0.6)

        for i, match in enumerate(self.__matches):
            if match:
                try:
                    self.__activeUser = self.__users[i % self.__users.__len__()]
                    self.__activeUserIndex = i % self.__users.__len__()
                except Exception as e:
                    print(e) 
                    self.__activeUser = None
                    self.__activeUserIndex = -1
                break
            else:
                self.__activeUser = None

        if self.__activeUser is None:
            return

        if self.__image_face_locations.__len__() > 1:
            for i, location in enumerate(self.__image_face_locations):
                if i == self.__activeUserIndex:
                    continue
                self.__unknown_face_locations.append(location)

            for unknown in self.__unknown_face_locations:
                if self.__low_res:
                    cv2.rectangle(image, (unknown[3] * 4, unknown[0] * 4),
                                  (unknown[1] * 4, unknown[2] * 4), (0, 0, 0), -1)
                else:
                    cv2.rectangle(
                        image, (unknown[3], unknown[0]), (unknown[1], unknown[2]), (0, 0, 0), -1)
                    

    def __reset_vars(self):
        self.__image_face_locations = []
        self.__image_face_encodings = []
        self.__matches = []
        self.__activeUser = None
        self.__activeUserIndex = -1
        
    def getUser(self):
        return self.__activeUser
        
'''        
fr = FaceRecognizer(low_res=True)

cap = cv2.VideoCapture(0)

fr.addUser("Yigit", "train_img/yigit.jpg")
fr.addUser("Ahmet", "train_img/ahmet.jpg")
fr.addUser("Seyit", "train_img/seyit.jpg")
fr.addUser("Arda", "train_img/arda.jpg")

while True:
    image = cap.read()[1]
    image = fr.eventLoop(image)
    cv2.imshow("Test", image)
    
    if fr.__activeUser != None:
        print(fr.__activeUser.name)
    
    if cv2.waitKey(1) & 0xFF == ord('q') or cv2.getWindowProperty("Test", cv2.WND_PROP_VISIBLE) == False:
        cap.release()
        break
'''
