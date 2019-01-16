from threading import Thread, Lock, Condition
import time


class PublisherThread(Thread):

    __publisher = None
    __queue = None
    __lock = None
    __data = None
    __publish = None
    __delay = None
    __max_publish_workers = None
    __task_condition = Condition()
    __running_workers = 0

    def __init__(self, publisher, data, publish, delay=1, __max_publish_workers=None):
        Thread.__init__(self)

        self.__publisher = publisher
        self.__queue = []
        self.__lock = Lock()
        self.__data = data
        self.__publish = publish
        self.__delay = delay
        self.__max_publish_workers = __max_publish_workers

    def schedule(self, payload):
        self.__lock.acquire()
        self.__queue.append(payload)
        self.__lock.release()

    def __worker(self, data):
        print("workers count - {}".format(self.__running_workers))
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
            else:
                self.__publish(self.__publisher, data_to_publish)

            time.sleep(self.__delay)
