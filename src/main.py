import FaceRecognizer
import FaceMesh
import TouchMenu

fr = FaceRecognizer.FaceRecognizer(low_res=True, number_of_frames_to_skip=20)
fm = FaceMesh.FaceMesh()
tm = TouchMenu.TouchMenu()