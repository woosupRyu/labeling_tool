import paho.mqtt.client as mqtt
import json


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connected OK")
    else:
        print("Bad connection Returned code=", rc )


def on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))

def on_publish(client, userdata, mid):

    print("In on_pub callback mid= ", mid)

class mqtt_connector():
    def __init__(self, ip_address, port):
        self.client = mqtt.Client()
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        self.client.on_publish = on_publish
        self.client.connect(ip_address, port, keepalive=10)

    def collect_dataset(self, env_id, image_type):
        self.client.publish(env_id, json.dumps
            ({"msg_group_type" :"cmd" ,"type" :"collect_dataset" ,"env_id" :"20001", "image_type" :"1"}), 1)
