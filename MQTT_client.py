import paho.mqtt.client as mqtt
import json

class mqtt_callback():
    def __init__(self, device_id, image_id):
        self.device_id = device_id
        self.image_id = image_id
        
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("connected OK")
        else:
            print("Bad connection Returned code=", rc)


    def on_disconnect(self, client, userdata, flags, rc=0):
        print(str(rc))


    def on_publish(self, client, userdata, mid):
        print("In on_pub callback mid= ", mid)

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print("subscribed: " + str(mid) + " " + str(granted_qos))

    def on_message(self, client, userdata, message):
        print('class method device_id : ', self.device_id)
        if message.topic == "device_operation_vending_web":
            data = json.loads(str(message.payload.decode("utf-8")))
            if data['ret_code'] == "0000":
                print('data collect success')
                self.image_id = data['msg']
            else:
                print('data collect fail')
                self.image_id = None
        client.disconnect()
        
    def get_result(self):
        return self.image_id

class mqtt_connector(mqtt_callback):
    def __init__(self, ip_address, port, device_id):
        super(mqtt_connector, self).__init__(device_id, 0)
        self.ip = ip_address
        self.port = port
        self.mutexlock = True
        
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message
        

    def collect_dataset(self, env_id, image_type):
        if self.mutexlock:
            self.mutexlock = False
            self.client.connect(self.ip, self.port)
            self.client.publish(env_id, json.dumps({"msg_group_type":"cmd","type":"collect_dataset","env_id":str(env_id), "image_type":str(image_type)}), 1)
            self.client.subscribe('device_operation_vending_web', 0)
            self.client.loop_forever()
            self.mutexlock = True
        else:
            print('door already open')
    
     
    
        
