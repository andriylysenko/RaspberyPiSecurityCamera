import cv2
import detector.MotionDetector as md
import publisher.PublisherThread as publisher
import publisher.MediaFirePublisher as mfp


def max_box(boxes):
    if len(boxes) > 0:
        mbox = boxes[0]
        print boxes
        for box in boxes:
            (x, y, w, h) = box
            (mx, my, mw, mh) = mbox
            mbox = (min(mx, x), min(my, y), max(mw, w), max(mh, h))
        return mbox
    return None

def publish(publisher, data):
    (mbox, frame) = data
    publisher.upload("IMG_20150801_180120.jpg", "/Tmp/test.jpg")

vs = cv2.VideoCapture(0)

cv2.namedWindow("out_img", cv2.WINDOW_NORMAL)

(grabbed, frame) = vs.read()
motion_detector = md.MotionDetector(frame)

publisher_worker = publisher.PublisherThread(mfp.MediaFirePublisher("username", "password"),
                                             lambda q : q.pop(0), publish, 0.1)
publisher_worker.start()

while True:
    (grabbed, frame) = vs.read()
    boxes = motion_detector.detect(frame)
    mbox = max_box(boxes)
    if mbox:
        (x, y, w, h) = mbox
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        publisher_worker.schedule((mbox, frame))
    cv2.imshow('out_img', frame)
    cv2.waitKey(1)

cv2.destroyAllWindows()

