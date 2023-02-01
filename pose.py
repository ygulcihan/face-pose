import PoseDetector

pd = PoseDetector.PoseDetector("Head Position", 0)

pd.detect_confidence = 0.7
pd.track_confidence = 0.7
pd.angle_threshold = 17

pd.draw_face_landmarks = True
pd.draw_nose_vector = True

pd.start()
