import cv2


class TensorObjectDetector:
    __net = None

    def __init__(self, netWeightsPath, netConfigPath):
        self.__net = cv2.dnn.readNetFromTensorflow(netWeightsPath, netConfigPath)

    def detect(self, frame):
        blob = cv2.dnn.blobFromImage(frame, swapRB=True, crop=False)
        self.__net.setInput(blob)
        (boxes, masks) = self.__net.forward(["detection_out_final", "detection_masks"])
        return boxes

