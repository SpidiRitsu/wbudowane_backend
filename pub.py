import paho.mqtt.client as mqtt
import time

broker_url = "spodo.pl"
broker_port = 1883

client = mqtt.Client()
client.connect(broker_url, broker_port)

client.publish(topic="Room3", payload="1P", qos=1, retain=False)
time.sleep(1)
client.publish(topic="Room3", payload="0P", qos=1, retain=False)
# client.publi
# client.publish(topic="Room1", payload="62.4H", qos=1, retain=False)
# time.sleep(0.5)
# client.publish(topic="Room1", payload="93.4L", qos=1, retain=False)