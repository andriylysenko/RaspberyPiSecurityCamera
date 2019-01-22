from threading import Thread, Lock, Condition
import time
import logging


class PublisherThread(Thread):

    __name = None
    __publisher = None
    __queue = None
    __lock = None
    __data = None
    __publish = None
    __delay = None
    __max_publish_workers = None
    __task_condition = Condition()
    __running_workers = 0

    def __init__(self, name,  publisher, data, publish, delay=1, __max_publish_workers=None):
        Thread.__init__(self)

        self.__name = name
        self.__publisher = publisher
        self.__queue = []
        self.__lock = Lock()
        self.__data = data
        self.__publish = publish
        self.__delay = delay
        self.__max_publish_workers = __max_publish_workers

    def schedule(self, payload):
        queue_size = None

        self.__lock.acquire()
        queue_size = len(self.__queue)
        self.__queue.append(payload)
        self.__lock.release()

        logging.info("Task scheduled for publisher {}; queue size={}".format(self.__name, queue_size))

    def __worker(self, data):
        self.__publish(self.__publisher, data)
        with self.__task_condition:
            self.__running_workers = self.__running_workers - 1
            self.__task_condition.notifyAll()

    def run(self):
        while True:
            self.__lock.acquire()
            data_to_publish = self.__data(self.__queue)
            self.__lock.release()
            if self.__max_publish_workers:
                with self.__task_condition:
                    while self.__running_workers >= self.__max_publish_workers:
                        self.__task_condition.wait()
                    self.__running_workers = self.__running_workers + 1
                    t = Thread(target=self.__worker, args=[data_to_publish])
                    t.daemon = True
                    t.start()
                    logging.info("Worker created for publisher {}; active={}".format(self.__name, self.__running_workers))
            else:
                self.__publish(self.__publisher, data_to_publish)

            time.sleep(self.__delay)
