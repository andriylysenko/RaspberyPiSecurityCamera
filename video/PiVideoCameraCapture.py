from picamera.array import PiRGBArray
from picamera import PiCamera


class PiVideoCameraCapture:

    __camera = None
    __rawCapture = None
    __format = None

    def __init__(self, resolution=(640, 480), frameset=32, format="bgr"):
        self.__camera = PiCamera()
        self.__camera.resolution = resolution
        self.__camera.framerate = frameset
        self.__rawCapture = PiRGBArray(self.__camera, size=resolution)
        self.__format = format

    def capture(self):
        self.__rawCapture.truncate(0)
        self.__camera.capture(self.__rawCapture, format=self.__format)
        return self.__rawCapture.array
