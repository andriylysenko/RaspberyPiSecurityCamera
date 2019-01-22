from mediafire.client import (MediaFireClient, File, Folder, ResourceNotFoundError)
from mediafire.uploader import (UploadError)
import os
import Queue
import logging


class MediaFirePublisher:

    __pool = None

    def __init__(self, user, password, max_clients=1):
        self.__max_clients = max_clients
        self.__pool = Queue.Queue(max_clients)
        [self.__pool.put(self.__get_client(user, password)) for i in range(max_clients)]

    def upload(self, source, destination):
        client = self.__pool.get()
        try:
            self.__create_path(client, destination)
            destination = "mf:" + destination
            client.upload_file(source, destination)
        except UploadError as e:
            logging.info("Upload error: {}".format(e))
        finally:
            self.__pool.put(client)

    def __get_client(self, user, password):
        client = MediaFireClient()
        client.login(email=user, password=password, app_id='42511')
        return client

    def __create_path(self, client, path):
        path = "mf:" + os.path.dirname(path)
        client.create_folder(path, recursive=True)
