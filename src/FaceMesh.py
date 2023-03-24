import cv2
import mediapipe as mp
import numpy as np
import GestureRecognizer

detect_confidence = 0.7
track_confidence = 0.7
pitch = 0
yaw = 0

__angle_coefficient__ = 1.0

__FACE_OUTLINE_INDEXES__ = [33, 263, 1, 61, 291, 199]
__FACE_MESH__ = mp.solutions.face_mesh.FaceMesh(min_detection_confidence=detect_confidence,
                                                min_tracking_confidence=track_confidence)
__DRAWING_SPEC__ = mp.solutions.drawing_utils.DrawingSpec(
    thickness=1, circle_radius=1)


def __init__(angle_coefficient=1.0):

    global __angle_coefficient__
    __angle_coefficient__ = angle_coefficient


def eventLoop(image):

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False  # To pass by reference
    results = __FACE_MESH__.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    img_h = image.shape[0]
    img_w = image.shape[1]

    face_3d = []
    face_2d = []

    if results.multi_face_landmarks:

        for face_landmarks in results.multi_face_landmarks:
            
            face = []
            
            # Get the indexes of each facial landmark
            for idx, lm in enumerate(face_landmarks.landmark):
                if idx == 1:
                    nose_2d = (lm.x * img_w, lm.y * img_h)

                x = int(lm.x * img_w)
                y = int(lm.y * img_h)
                
                face.append([x, y])
                
                # Face outline coordinates
                if idx in __FACE_OUTLINE_INDEXES__:
                    face_2d.append([x, y])
                    face_3d.append([x, y, lm.z])
            
            # Convert it to NumPy array
            face_2d = np.array(face_2d, dtype=np.float64)

            # Convert it to NumPy array
            face_3d = np.array(face_3d, dtype=np.float64)

            cam_matrix = np.array([[img_w, 0, img_h / 2],
                                   [0, img_w, img_w / 2],
                                   [0, 0, 1]])

            # Solve PnP
            rot_vec = cv2.solvePnP(
                face_3d, face_2d, cam_matrix, 0)[1]

            # Get rotational matrix
            rotation_matrix = cv2.Rodrigues(rot_vec)[0]

            rot_ratios = cv2.RQDecomp3x3(rotation_matrix)[0]

            # Calculate the head rotation in degrees
            __calculateHeadRotation(rot_ratios)
            
            GestureRecognizer.isEyebrowRaised(face, pitch, yaw)


def __calculateHeadRotation(ratios):

    global pitch, yaw

    pitch = np.round(
        ratios[0] * 180 * np.pi * __angle_coefficient__)
    yaw = np.round(
        ratios[1] * 180 * np.pi * __angle_coefficient__)


# For testing purposes
cap = cv2.VideoCapture(0)

while True:
    image = cv2.flip(cap.read()[1], 1)  # Flip the image horizontally
    eventLoop(image)
    # Add the text on the image
    cv2.putText(image, "Pitch: " + str(int(pitch)), (450, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.putText(image, "Yaw: " + str(int(yaw)), (450, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.imshow("Face Mesh", image)

    pressedKey = cv2.waitKey(1) & 0xFF

    if pressedKey == ord('q') or pressedKey == 27 or cv2.getWindowProperty("Face Mesh", cv2.WND_PROP_VISIBLE) < 1:
        break