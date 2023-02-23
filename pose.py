import PoseDetector

pd = PoseDetector.PoseDetector("Head Position", 0)

pd.detect_confidence = 0.7
pd.track_confidence = 0.7
pd.angle_threshold = 15
pd.angle_coefficient = 2.5

pd.draw_face_landmarks = False
pd.draw_nose_vector = True
pd.draw_face_box = False

pd.start()
