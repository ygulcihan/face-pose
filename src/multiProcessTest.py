import multiprocessing
import queue
import cv2
import FaceRecognizer

fr = FaceRecognizer.FaceRecognizer(low_res=True, number_of_frames_to_skip=0)

fr.addUser("Yigit", "train_img/yigit.jpg")
fr.addUser("Yigit", "train_img/yigit-gozluklu.jpg")


def face_recognition_worker(image_queue, result_queue, stop_event):
    while not stop_event.is_set():
        try:
            image = image_queue.get(timeout=1)  # Get an image from the queue with a timeout
        except queue.Empty:
            continue

        # Perform face recognition on the image
        fr.eventLoop(image)

        if fr.getUser() is not None:
            result = fr.getUser().name
        else:
            result = None
        # Put the result in the result queue
        result_queue.put(result)

def display_frames(image_queue, stop_event):
    while not stop_event.is_set():
        try:
            frame = image_queue.get(timeout=1)
            cv2.imshow("Image", frame)
            try:
                if cv2.waitKey(1) == ord('q') or not cv2.getWindowProperty("Image", cv2.WND_PROP_VISIBLE):
                    stop_event.set()
            except Exception:
                continue
        except queue.Empty:
            continue

if __name__ == "__main__":
    max_queue_size = 10

    manager = multiprocessing.Manager()
    image_queue = manager.Queue(maxsize=max_queue_size)
    result_queue = manager.Queue()
    stop_event = multiprocessing.Event()

    recognition_process = multiprocessing.Process(target=face_recognition_worker, args=(image_queue, result_queue, stop_event))
    recognition_process.start()

    display_process = multiprocessing.Process(target=display_frames, args=(image_queue, stop_event))
    display_process.start()

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        if image_queue.full():
            image_queue.get()
        image_queue.put(frame)

        if not result_queue.empty():
            result = result_queue.get()
            # Process the face recognition result
            if result is not None:
                print(result)

        if stop_event.is_set():
            cap.release()
            cv2.destroyAllWindows()
            break
