import cv2
import mediapipe as mp
import numpy as np
import time


class PoseDetector:

    angle_threshold = 15
    window_title = "Pose Detector"
    draw_face_landmarks = False
    print_fps = False
    draw_fps = False
    draw_nose_vector = False
    __cap__ = None
    __face_mesh__ = None
    __mp_face_mesh__ = None
    __drawing_spec__ = None
    __mp_drawing__ = None
    __pitch__ = 0
    __yaw__ = 0
    __z__ = 0
    detect_confidence = 0.5
    track_confidence = 0.5
    __text__ = ""

    def convertToDegrees(self, angles):

        self.__pitch__ = np.round(angles[0] * 180 * np.pi)
        self.__yaw__ = np.round(angles[1] * 180 * np.pi)
        self.__z__ = np.round(angles[2] * 180 * np.pi)

    def __init__(self, window_title, camera=0):
        self.window_title = window_title
        self.__mp_face_mesh__ = mp.solutions.face_mesh
        self.__face_mesh__ = self.__mp_face_mesh__.FaceMesh(min_detection_confidence=self.detect_confidence,
                                                            min_tracking_confidence=self.track_confidence)

        self.__mp_drawing__ = mp.solutions.drawing_utils

        self.__drawing_spec__ = self.__mp_drawing__.DrawingSpec(
            thickness=1, circle_radius=1)

        self.__cap__ = cv2.VideoCapture(camera)

    def start(self):
        while self.__cap__.isOpened():
            image = self.__cap__.read()[1]

            startTime = time.time()

            # Flip the image horizontally for a later selfie-view display
            # Also convert the color space from BGR to RGB
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
                                nose_3d = (lm.x * img_w, lm.y *
                                           img_h, lm.z * 3000)

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
                                           [0,     0,      1]])

                    # Solve PnP
                    success, rot_vec, trans_vec = cv2.solvePnP(
                        face_3d, face_2d, cam_matrix, 0)

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
                    p2 = (int(nose_2d[0] + self.__yaw__ * 10) , int(nose_2d[1] - self.__pitch__ * 10))
                    cv2.line(image, p1, p2, (255, 0, 0), 3)

            cv2.imshow(self.window_title, image)
                
            # Esc or Close Window to exit
            if cv2.waitKey(5) & 0xFF == 27 or cv2.getWindowProperty(self.window_title, cv2.WND_PROP_VISIBLE) == False:
                break

        self.__cap__.release()
