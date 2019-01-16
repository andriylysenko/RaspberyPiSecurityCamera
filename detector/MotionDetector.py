import cv2


class MotionDetector:

    __avg_img = None

    def __init__(self, start_frame):
        start_frame = cv2.cvtColor(start_frame, cv2.COLOR_BGR2GRAY)
        start_frame = cv2.GaussianBlur(start_frame, (21, 21), 0)
        self.__avg_img = start_frame.copy().astype("float")

    def detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        cv2.accumulateWeighted(gray, self.__avg_img, 0.4)
        frame_delta = cv2.absdiff(gray, cv2.convertScaleAbs(self.__avg_img))

        thresh = cv2.threshold(frame_delta, 5, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]
        boxes = list()
        for c in cnts:
            if cv2.contourArea(c) < 4000:
                continue
            boxes.append(cv2.boundingRect(c))

        return boxes
