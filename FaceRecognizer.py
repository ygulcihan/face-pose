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

    activeUser = None

    def __init__(self, low_res=False, number_of_frames_to_skip=15):
        self.__low_res = low_res
        self.__nrOfFramesToSkip = number_of_frames_to_skip

    def addUser(self, name, image_path):
        newUser = User.User(name, image_path)
        self.__users.append(newUser)
        self.__known_face_encodings.append(newUser.face_encoding)

    def eventLoop(self, image):
        
        self.__reset_vars()

        if self.__skipped_frames < self.__nrOfFramesToSkip:
            self.__skipped_frames += 1
            return image
        
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
                self.__known_face_encodings, encoding)

        for i, match in enumerate(self.__matches):
            if match:
                self.activeUser = self.__users[i]
                self.__activeUserIndex = i
                break

        if self.activeUser is None:
            return image

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
                    
        return image

    def __reset_vars(self):
        self.__image_face_locations = []
        self.__image_face_encodings = []
        self.__matches = []
        self.activeUser = None
        self.__activeUserIndex = -1
