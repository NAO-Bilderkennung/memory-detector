from cv2 import VideoCapture, CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT


def get_camera():
    capture = VideoCapture(0)  # 0 == default webcam

    capture.set(CAP_PROP_FRAME_WIDTH, 640)
    capture.set(CAP_PROP_FRAME_HEIGHT, 480)

    w, h = capture.get(CAP_PROP_FRAME_WIDTH), capture.get(CAP_PROP_FRAME_HEIGHT)
    w, h = int(w), int(h)

    return capture, w, h
