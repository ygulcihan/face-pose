import cv2
import mediapipe as mp
import numpy as np
import face_recognition
from imutils.video import VideoStream
import time


# TODO: Block non user faces

class PoseDetector:
    angle_threshold = 15
    window_title = "Pose Detector"
    draw_face_landmarks = False
    draw_nose_vector = False
    draw_face_box = False
    user_name = "Yigit"
    detect_confidence = 0.5
    track_confidence = 0.5
    angle_coefficient = 1

    __cap__ = None
    __face_mesh__ = None
    __mp_face_mesh__ = None
    __drawing_spec__ = None
    __mp_drawing__ = None
    __pitch__ = 0
    __yaw__ = 0
    __z__ = 0
    __text__ = ""
    __authenticated__ = False
    __process_this_frame__ = True
    __known_face_names__ = []
    __known_face_encodings__ = []
    __known_face_index__ = -1
    __user_image__ = None
    __user_face_encoding__ = None
    __face_locations__ = []
    __unknown_face_locations__ = []
    __matches__ = []
    __face_encodings__ = []
    __face_names__ = []

    def convertToDegrees(self, angles):

        self.__pitch__ = np.round(
            angles[0] * 180 * np.pi * self.angle_coefficient)
        self.__yaw__ = np.round(
            angles[1] * 180 * np.pi * self.angle_coefficient)
        self.__z__ = np.round(angles[2] * 180 * np.pi * self.angle_coefficient)

    def __init__(self, window_title, camera=0):
        self.window_title = window_title
        self.__mp_face_mesh__ = mp.solutions.face_mesh
        self.__face_mesh__ = self.__mp_face_mesh__.FaceMesh(min_detection_confidence=self.detect_confidence,
                                                            min_tracking_confidence=self.track_confidence)

        self.__mp_drawing__ = mp.solutions.drawing_utils

        self.__drawing_spec__ = self.__mp_drawing__.DrawingSpec(
            thickness=1, circle_radius=1)

        self.__cap__ = cv2.VideoCapture(camera)
        # self.__cap__ = VideoStream(src=camera).start()

    def start(self):
        # Load a sample picture and learn how to recognize it.
        self.__user_image__ = face_recognition.load_image_file(
            "train_img/yigit2.jpg")
        self.__user_face_encoding__ = face_recognition.face_encodings(
            self.__user_image__)[0]

        # Create arrays of known face encodings and their names
        self.__known_face_encodings__ = [
            self.__user_face_encoding__
        ]
        self.__known_face_names__ = [
            self.user_name
        ]

        while True:

            image = self.__cap__.read()[1]
            # image = self.__cap__.read()

            if (not self.__authenticated__):
                image = self.face_recog(image)
                cv2.putText(image, "Not Authenticated", (700, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
                image = cv2.resize(image, (1366, 720))

            else:
                image = cv2.resize(image, (1366, 720))
                image = self.head_pose(image)
                cv2.putText(image, "Authenticated", (800, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
                cv2.putText(image, f"User: {self.__face_names__[0]}", (800, 130), cv2.FONT_HERSHEY_SIMPLEX, 2,
                            (255, 0, 0), 2)

            cv2.imshow(self.window_title, image)

            # Esc or Close Window to exit
            if cv2.waitKey(5) & 0xFF == 27 or cv2.getWindowProperty(self.window_title, cv2.WND_PROP_VISIBLE) == False:
                break

        self.__cap__.release()

    def head_pose(self, pimage):

        image = pimage

        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

        # To improve performance for Mp
        image.flags.writeable = False

        # Get the result
        results = self.__face_mesh__.process(image)

        # Set image writable for opencv
        image.flags.writeable = True

        # Convert the color space from RGB to BGR
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        img_h, img_w, img_c = image.shape
        face_3d = []
        face_2d = []

        if results.multi_face_landmarks:

            for face_landmarks in results.multi_face_landmarks:
                # Get the indexes of each facial landmark
                for idx, lm in enumerate(face_landmarks.landmark):
                    # Face outline coordinates
                    if idx == 33 or idx == 263 or idx == 1 or idx == 61 or idx == 291 or idx == 199:
                        if idx == 1:
                            nose_2d = (lm.x * img_w, lm.y * img_h)

                        self.__pitch__, self.__yaw__ = int(
                            lm.x * img_w), int(lm.y * img_h)

                        # Get the 2D Coordinates
                        face_2d.append([self.__pitch__, self.__yaw__])

                        # Get the 3D Coordinates
                        face_3d.append(
                            [self.__pitch__, self.__yaw__, lm.z])

                # Convert it to the NumPy array
                face_2d = np.array(face_2d, dtype=np.float64)

                # Convert it to the NumPy array
                face_3d = np.array(face_3d, dtype=np.float64)

                cam_matrix = np.array([[img_w, 0, img_h / 2],
                                       [0, img_w, img_w / 2],
                                       [0, 0, 1]])

                # Solve PnP
                rot_vec = cv2.solvePnP(
                    face_3d, face_2d, cam_matrix, 0)[1]

                # Get rotational matrix
                # returns [rotation matrix, jacobian]
                rmat = cv2.Rodrigues(rot_vec)[0]

                # Get angles
                angles = cv2.RQDecomp3x3(rmat)[0]

                # Calculate the head rotation in degrees
                self.convertToDegrees(angles)

                # See where the user's head tilting
                if self.__yaw__ < -self.angle_threshold:
                    self.__text__ = "Looking Left"
                elif self.__yaw__ > self.angle_threshold:
                    self.__text__ = "Looking Right"
                elif self.__pitch__ < -self.angle_threshold:
                    self.__text__ = "Looking Down"
                elif self.__pitch__ > self.angle_threshold:
                    self.__text__ = "Looking Up"
                else:
                    self.__text__ = "Forward"

                # Add the text on the image
                cv2.putText(image, self.__text__, (20, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
                cv2.putText(image, "Pitch: " + str(int(self.__pitch__)), (450, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                cv2.putText(image, "Yaw: " + str(int(self.__yaw__)), (450, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            if self.draw_face_landmarks:
                self.__mp_drawing__.draw_landmarks(
                    image=image,
                    landmark_list=face_landmarks,
                    connections=self.__mp_face_mesh__.FACEMESH_CONTOURS,
                    landmark_drawing_spec=self.__drawing_spec__,
                    connection_drawing_spec=self.__drawing_spec__)

            if self.draw_nose_vector:
                p1 = (int(nose_2d[0]), int(nose_2d[1]))
                p2 = (int(nose_2d[0] + self.__yaw__ * 10),
                      int(nose_2d[1] - self.__pitch__ * 10))
                cv2.line(image, p1, p2, (255, 0, 0), 3)

            if self.draw_face_box:
                self.__face_locations__ = face_recognition.face_locations(
                    cv2.resize(image, (0, 0), fx=0.25, fy=0.25), model="hog")

                # Display the results
                for (top, right, bottom, left), name in zip(self.__face_locations__, self.__face_names__):
                    # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4

                    # Draw a box around the face
                    cv2.rectangle(image, (left, top),
                                  (right + 10, bottom + 10), (0, 0, 255), 2)

                    # Draw a label with a name below the face
                    cv2.rectangle(image, (left, bottom - 25),
                                  (right + 10, bottom + 10), (0, 0, 205), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(image, name, (left + 16, bottom + 4),
                                font, 1.1, (255, 255, 255), 1)

        else:
            self.__authenticated__ = False

        return image

    def face_recog(self, pImage):

        image = pImage

        self.__face_names__ = []

        # Resize image of video to 1/4 size for faster face recognition processing
        #small_frame = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
        #
        small_frame = image
        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Find all the faces and face encodings in the current image of video
        self.__face_locations__ = face_recognition.face_locations(
            rgb_small_frame, model="hog")
        self.__face_encodings__ = face_recognition.face_encodings(
            rgb_small_frame, self.__face_locations__)

        self.__face_names__ = []
        
        name = "Unknown"

        for face_encoding in self.__face_encodings__:
            # See if the face is a match for the known face(s)
            self.__matches__ = face_recognition.compare_faces(
                self.__known_face_encodings__, face_encoding)

            
            # If a match was found in known_face_encodings, just use the first one.
            if True in self.__matches__:
                first_match_index = self.__matches__.index(True)
                name = self.__known_face_names__[first_match_index]
                if self.__known_face_index__ == -1:
                    self.__known_face_index__ = self.__face_encodings__.index(face_encoding)
            
            # Or instead, use the known face with the smallest distance to the new face
            '''
            face_distances = face_recognition.face_distance(self.__known_face_encodings__, face_encoding)
            best_match_index = np.argmin(face_distances)
            if self.__matches__[best_match_index]:
                name = self.__known_face_names__[best_match_index]
            '''
        for location in self.__face_locations__:
            self.__unknown_face_locations__.append(location)
            if (self.__known_face_index__ != -1):
                if location == self.__face_locations__[self.__known_face_index__]:
                    self.__unknown_face_locations__.remove(location)

        if self.__unknown_face_locations__ != [] and self.__known_face_index__ != -1:
            for unknown in self.__unknown_face_locations__:
                #cv2.rectangle(image, (unknown[3] * 4, unknown[0] * 4), (unknown[1] * 4, unknown[2] * 4), (0, 0, 0), -1)
                cv2.rectangle(image, (unknown[3], unknown[0]), (unknown[1], unknown[2]), (0, 0, 0), -1)
        

        self.__face_names__.append(name)

        self.__process_this_frame__ = not self.__process_this_frame__

        if self.__face_names__ != [] and self.__face_names__[0] != "Unknown":
            self.__authenticated__ = True

        image = cv2.flip(image, 1)
        self.__matches__ = []
        self.__face_encodings__ = []
        self.__face_locations__ = []
        self.__unknown_face_locations__ = []
        self.__known_face_index__ = -1
        return image
