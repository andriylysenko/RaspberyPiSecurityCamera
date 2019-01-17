# -*- coding: utf-8 -*-

import cv2
import time
import  detector.MotionDetector as md
import detector.TensorObjectDetector as tod
import detector.CaffeObjectDetector as cod
import processor.FrameProcessor as fp
import publisher.MqttPublisher as p
import publisher.PublisherThread as publisher


def data_to_publish(queue):
    publish_set = set()
    while len(queue) > 0:
        publish_set.add(queue.pop(0))
    return publish_set


def publish(publisher, data):
    for m in data:
        publisher.publish("video/event", m)
        print m
        time.sleep(1)


#weightsPath = "rcnn/frozen_inference_graph.pb"
#configPath = "rcnn/mask_rcnn_inception_v2_coco_2018_01_28.pbtxt"
#labels1Path = "rcnn/object_detection_classes_coco.txt"
#labels2Path = "rcnn/object_detection_classes_coco_ru.txt"

weightsPath = "mobilenet/MobileNetSSD_deploy.caffemodel"
configPath = "mobilenet/MobileNetSSD_deploy.prototxt.txt"
labels1Path = "mobilenet/object_detection_classes.txt"
labels2Path = "mobilenet/object_detection_classes.txt"

labels = open(labels1Path).read().strip().split("\n")
labels_ru = open(labels2Path).read().strip().split("\n")

vs = cv2.VideoCapture(0)
(grabbed, frame) = vs.read()

motion_detector = md.MotionDetector(frame)
#object_detector = tod.TensorObjectDetector(weightsPath, configPath)
object_detector = cod.CaffeObjectDetector(weightsPath, configPath)
processor = fp.FrameProcessor(motion_detector, object_detector, labels)

cv2.namedWindow("out_img", cv2.WINDOW_NORMAL)

publisher_worker = publisher.PublisherThread(p.MqttPublisher("1.2.3.4", 1883, "user", "password"),
                                             data_to_publish, publish, 10)
publisher_worker.start()

while True:
    (grabbed, img) = vs.read()
    #img = cv2.resize(frame, (0, 0), fx=0.8, fy=0.8)
    (out_img, out_labels_idxs) = processor.process(img)

    for i in out_labels_idxs:
        publisher_worker.schedule(labels_ru[i])

    cv2.imshow('out_img', out_img)
    cv2.waitKey(1)

cv2.destroyAllWindows()



