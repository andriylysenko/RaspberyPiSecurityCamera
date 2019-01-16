import numpy as np
import cv2


class FrameProcessor:

    __labels = None
    __motion_detector = None
    __object_detector = None

    def __init__(self, motion_detector, object_detector, labels):
        self.__motion_detector = motion_detector
        self.__object_detector = object_detector
        self.__labels = labels

    def process(self, frame):
        pred_label_idxs = list()
        motion_boxes = self.__motion_detector.detect(frame)
        motion_box = self.__get_max_box(motion_boxes)
        if motion_box is not None:
            (mx, my, mw, mh) = motion_box
            boxes = self.__object_detector.detect(frame)
            for i in range(0, boxes.shape[2]):
                class_id = int(boxes[0, 0, i, 1])
                prob = boxes[0, 0, i, 2]

                if prob < 0.8:
                    continue

                (height, width) = frame.shape[:2]
                box = boxes[0, 0, i, 3:7] * np.array([width, height, width, height])
                (start_x, start_y, end_x, end_y) = box.astype("int")

                if self.__intersects((start_x, start_y, end_x, end_y), (mx, my, mx + mw, my + mh)):
                    color = [255, 0, 0]
                    cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), color, 2)
                    #cv2.rectangle(frame, (mx, my), (mx + mw, my + mh), (0, 255, 0), 2)
                    text = "{}: {:.4f}".format(self.__labels[class_id], prob)
                    cv2.putText(frame, text, (start_x, start_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                    pred_label_idxs.append(class_id)
        return frame, pred_label_idxs

    def __get_max_box(self, boxes):
        if len(boxes) == 0:
            return None

        max_box = boxes[0]
        for box in boxes:
            (x, y, w, h) = box
            (mx, my, mw, mh) = max_box
            max_box = (min(mx, x), min(my, y), max(mw, w), max(mh, h))

        return max_box

    def __intersects(self, box1, box2):
        return not ((box1[0] > box2[2] or box1[2] < box2[0]) or (box1[1] > box2[3] or box1[3] < box2[1]))
