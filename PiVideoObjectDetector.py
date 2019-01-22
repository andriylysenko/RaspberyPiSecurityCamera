# -*- coding: utf-8 -*-

import sys
import logging
import cv2
import time
import datetime
import os
import tempfile
import argparse
import yaml
import  detector.MotionDetector as md
import detector.CaffeObjectDetector as cod
import processor.FrameProcessor as fp
import publisher.MqttPublisher as p
import publisher.MediaFirePublisher as mfp
import publisher.PublisherThread as publisher
import video.PiVideoCameraCapture as picamera
import video.VideoCameraCapture as vcamera


def data_to_publish(queue):
    publish_set = set()
    while len(queue) > 0:
        (img, labels_idx, labels, now) = queue.pop(0)
        [publish_set.add(labels[i]) for i in labels_idx]
    return publish_set


def publish(publisher, data):
    for m in data:
        publisher.publish("video/event", m)
        logging.info("Publishing event: {}".format(m))
        time.sleep(1)


def media_data_to_publish(queue):
    if len(queue) > 0:
        (img, labels_idx, labels, now) = queue.pop(0)
        if len(labels_idx) > 0:
            return img, now
    return ()


def media_publish(publisher, data):
    if len(data) > 0:
        try:
            (image, now) = data
            filename = "{}-{}-{}-{}.jpg".format(now.hour, now.minute, now.second, now.microsecond)
            target = "/Secure/Camera/{}/{}/{}/{}".format(now.year, now.month, now.day, filename)
            source = "{}/{}".format(tempfile.gettempdir(), filename)
            logging.info("Uploading file: {}".format(target))
            cv2.imwrite(source, image)
            publisher.upload(source, target)
            os.remove(source)
            logging.info("Upload completed; file: {}".format(target))
        except Exception as e:
            logging.error("Upload error {}".format(e))


def get_frame_processor(net_config, frame, labels):
    motion_detector = md.MotionDetector(frame)
    object_detector = cod.CaffeObjectDetector(net_config["model"], net_config["config"])
    return fp.FrameProcessor(motion_detector, object_detector, labels)


def get_camera(video_config):
    if video_config["capture"] == "camera":
        return vcamera.VideoCameraCapture(0)
    elif video_config["capture"] == "picamera":
        return picamera.PiVideoCameraCapture(resolution=(video_config["picamera"]["resolution"]["width"], video_config["picamera"]["resolution"]["height"]),
                                             frameset=video_config["picamera"]["frameset"],
                                             format=video_config["picamera"]["format"])


def get_mqtt_publisher(mqtt_config):
    return publisher.PublisherThread("mqtt",
        p.MqttPublisher(mqtt_config["host"], mqtt_config["port"], mqtt_config["user"], mqtt_config["password"]),
            data_to_publish, publish, mqtt_config["publisher"]["delay"], mqtt_config["publisher"]["threads"])


def get_media_publisher(media_config):
    return publisher.PublisherThread("media fire",
        mfp.MediaFirePublisher(media_config["user"], media_config["password"], media_config["maxClients"]),
            media_data_to_publish, media_publish, media_config["publisher"]["delay"], media_config["publisher"]["threads"])


def main(config):
    logger = logging.getLogger()
    logger.info("Starting with config: {}".format(config))

    labels = open(config["net"]["labels"]).read().strip().split("\n")

    logger.info("Creating camera")
    camera = get_camera(config["video"])

    logger.info("Creating frame processor")
    processor = get_frame_processor(config["net"], camera.capture(), labels)

    logger.info("Adding publishers")
    publishers = list()
    publishers.append(get_mqtt_publisher(config["mqtt"]))
    publishers.append(get_media_publisher(config["mediafire"]))
    [pub.start() for pub in publishers]

    show_video_stream = config["showVideoStream"]
    if show_video_stream:
        cv2.namedWindow("out_img", cv2.WINDOW_NORMAL)

    while True:
        (out_img, out_labels_idxs) = processor.process(camera.capture())
        [pub.schedule((out_img, out_labels_idxs, labels, datetime.datetime.now())) for pub in publishers]

        if show_video_stream:
            cv2.imshow('out_img', out_img)
            cv2.waitKey(1)

    if show_video_stream:
        cv2.destroyAllWindows()


if __name__== "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ])

    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--config", type=str, required=True, help="path to yml config file")
    args = vars(ap.parse_args())
    config_file = args["config"]
    with open(config_file, 'r') as stream:
        try:
            main(yaml.safe_load(stream))
        except yaml.YAMLError as exc:
            logging.error("Config error {}".format(exc))
