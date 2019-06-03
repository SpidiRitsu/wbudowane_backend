import os
import paho.mqtt.client as mqtt
import time

# MQTT
broker_address = "spodo.pl"
broker_portno = 1883
client = mqtt.Client()
client.connect(broker_address, broker_portno)
# Out
channels = ['Room1', 'Room2', 'Room3']


def on_connect(client, userdata, flags, rc):
    for channel in channels:
        client.subscribe(channel)
        print('Subscribing to: {chan}'.format(chan=channel))
        time.sleep(0.5)


def _on_message(client, userdata, message):
    topic = message.topic
    message = message.payload.decode()
    msg_resolver(message, topic)


def msg_resolver(text, room):
    if text[1] == 'B':
        room += '_' + room[-1]
        relay = text[2]
        state = text[0]
        client.publish(topic=room, payload=str(relay + state))


client.on_connect = on_connect
client.on_message = _on_message

client.loop_forever()