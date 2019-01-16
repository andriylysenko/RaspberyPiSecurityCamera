import cv2


class CaffeObjectDetector:
    __net = None

    def __init__(self, net_weights_path, net_config_path):
        self.__net = cv2.dnn.readNetFromCaffe(net_config_path, net_weights_path)

    def detect(self, frame):
        frame = cv2.resize(frame, (300, 300))
        blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)
        self.__net.setInput(blob)
        boxes = self.__net.forward()
        return boxes