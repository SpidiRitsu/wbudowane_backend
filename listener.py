import paho.mqtt.client as mqtt
import time
import requests

# MQTT
broker_address = "spodo.pl"
broker_portno = 1883
client = mqtt.Client()
# client.connect(broker_address, broker_portno)
client.connect_async(broker_address, broker_portno)

# Out
channels = ['Room1', 'Room1_1', 'Room2', 'Room2_2', 'Room3', 'Room3_3']

# Routes
sensors = ['T', 'H', 'L']

routes = {
	"T": "temperature",
	"H": "humidity",
	"L": "luminosity"
}

def on_connect(client, userdata, flags, rc):
	for channel in channels:
		client.subscribe(channel)
		print('Subscribing to: {chan}'.format(chan=channel))
		time.sleep(0.5)

def on_message(client, userdata, message):
	message_r = message.payload.decode()
	print("Message Recieved:", message_r)
	data = {
		"value": float(message_r[:-1]),
		"room": message.topic
	}
	print('Sending data...')
	print(data)
	print(type(data['value']))
	r = requests.post(f"http://localhost:5000/{routes[message_r[-1]]}", json=data)
	print(r.status_code)
	print(r.headers)
	print(r.text)

client.on_connect = on_connect
client.on_message = on_message
# client.message_callback_add('Room1', on_message)

# client.loop_forever()
client.loop_start()
# for i in range(100):
	# print('WTF NIGGA')
while True:
	pass