import cv2


class VideoCameraCapture:

    __vc = None

    def __init__(self, source):
        self.__vc = cv2.VideoCapture(source)

    def capture(self):
        (grabbed, frame) = self.__vc.read()
        return frame
