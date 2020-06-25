import paho.mqtt.client as mqtt
import json


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connected OK")
    else:
        print("Bad connection Returned code=", rc)

def on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))

def on_publish(client, userdata, mid):
    print("In on_pub callback mid= ", mid)


def on_subscribe(client, userdata, mid, granted_qos):
    print("subscribed: " + str(mid) + " " + str(granted_qos))


def on_message(client, userdata, message):
    print("message received ", str(message.payload.decode("utf-8")))
    print("message topic=", message.topic)
    print("message qos=", message.qos)
    print("message retain flag=", message.retain)
    print("userdata=", userdata)
    if message.topic == "device_operation_vending_web":
        data = json.loads(str(message.payload.decode("utf-8")))
        if data['ret_code'] == "0000":
            client.disconnect()
        else:
            print('fail!')


class mqtt_connector():
    def __init__(self, ip_address, port):
        self.ip = ip_address
        self.port = port

        self.client = mqtt.Client()
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        self.client.on_publish = on_publish
        self.client.on_subscribe = on_subscribe
        self.client.on_message = on_message

    def collect_dataset(self, env_id, image_type):
        self.client.connect(self.ip, self.port)
        self.client.publish(env_id, json.dumps(
            {"msg_group_type": "cmd", "type": "collect_dataset", "env_id": "20001", "image_type": "1"}), 1)
        self.client.subscribe('device_operation_vending_web', 0)
        self.client.loop_forever()