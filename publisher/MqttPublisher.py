import time
import paho.mqtt.client as mqttclient


class MqttPublisher:

    __client = None
    __connected = False

    def __init__(self, hostname, port, user, password):
        self.__hostname = hostname
        self.__port = port
        self.__user = user
        self.__password = password

        self.__client = mqttclient.Client("pi_client")
        self.__client.username_pw_set(user, password=password)
        self.__client.on_connect = self.on_connect
        self.__client.connect(hostname, port=port)

        self.__client.loop_start()

        while not self.__connected:
            time.sleep(0.1)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.__connected = True

    def publish(self, topic, message):
        self.__client.publish(topic, message)
