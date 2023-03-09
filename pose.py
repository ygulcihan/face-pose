import PoseDetector

pd = PoseDetector.PoseDetector("Head Position", 0)

pd.cap_source = pd.eCaptureSource.IMUTILS

pd.detect_confidence = 0.7
pd.track_confidence = 0.7
pd.angle_threshold = 15
pd.angle_coefficient = 2.0

pd.draw_face_landmarks = False
pd.draw_nose_vector = True
pd.draw_face_box = False

pd.start()
