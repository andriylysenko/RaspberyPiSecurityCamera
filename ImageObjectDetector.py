# -*- coding: utf-8 -*-

import cv2
import detector.TensorObjectDetector as od
import processor.FrameProcessor as fp
import publisher.MqttPublisher as p

publisher = p.MqttPublisher("192.168.2.106", 1883, "openhab", "openhab_123")
#publisher.publish("video/event", "Лучших своих героев Л. Н. Толстой изображает во всей их душевной сложности, в непрерывных поисках истины, в стремлении к самосовершенствованию. Таковы князь Андрей, Пьер, Наташа, Николай, княжна Марья. Отрицательные герои лишены развития, динамики, движений души: Элен, Анатоль.")

weightsPath = "rcnn/frozen_inference_graph.pb"
configPath = "rcnn/mask_rcnn_inception_v2_coco_2018_01_28.pbtxt"
labels1Path = "rcnn/object_detection_classes_coco.txt"
labels2Path = "rcnn/object_detection_classes_coco_ru.txt"
img = cv2.imread("IMG_20181008_151406.jpg")
img = cv2.resize(img, (0,0), fx=0.2, fy=0.2)

labels = open(labels1Path).read().strip().split("\n")
labels_ru = open(labels2Path).read().strip().split("\n")
object_detector = od.ObjectDetector(weightsPath, configPath)
processor = fp.FrameProcessor(object_detector, labels)
(out_img, out_labels_idxs) = processor.process(img)

for i in out_labels_idxs:
    publisher.publish("video/event", "Обнаружен " + labels_ru[i] + ".")
    print labels_ru[i]

#publisher = p.MqttPublisher("localhost", 1883, "user", "password")
#publisher.publish("video/event", "test")

cv2.namedWindow("out_img", cv2.WINDOW_NORMAL)
cv2.imshow('out_img', out_img)
cv2.waitKey(0)
cv2.destroyAllWindows()


