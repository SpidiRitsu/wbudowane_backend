from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_socketio import SocketIO, send, emit

from email_notificator import send_doorbell_notification

import paho.mqtt.client as mqtt
import datetime
import os
import json
import re

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init SocketIO
socketio = SocketIO(app)
# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)
# MQTT
broker_address = "spodo.pl"
broker_portno = 1883
client = mqtt.Client()
client.connect_async(broker_address, broker_portno)

channels = ['Room1', 'Room1_1', 'Room2', 'Room2_2', 'Room3', 'Room3_3', 'Roommeteo']

# Models and Schemes
class Temperature(db.Model):
	__tablename__ = "temperature"

	id = db.Column(db.Integer, primary_key=True)
	value = db.Column(db.Float)
	room = db.Column(db.String)
	date = db.Column(db.String)

	def __init__(self, value, room):
		self.value = value
		self.room = room
		self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class TemperatureSchema(ma.Schema):
	class Meta:
		fields = ('id', 'value', 'room', 'date')

class Humidity(db.Model):
	__tablename__ = "humidity"

	id = db.Column(db.Integer, primary_key=True)
	value = db.Column(db.Float)
	room = db.Column(db.String)
	date = db.Column(db.String)

	def __init__(self, value, room):
		self.value = value
		self.room = room
		self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class HumiditySchema(ma.Schema):
	class Meta:
		fields = ('id', 'value', 'room', 'date')

class Luminosity(db.Model):
	__tablename__ = "luminosity"

	id = db.Column(db.Integer, primary_key=True)
	value = db.Column(db.Float)
	room = db.Column(db.String)
	date = db.Column(db.String)

	def __init__(self, value, room):
		self.value = value
		self.room = room
		self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class LuminositySchema(ma.Schema):
	class Meta:
		fields = ('id', 'value', 'room', 'date')

class Relays(db.Model):
	__tablename__ = "relays"

	id = db.Column(db.Integer, primary_key=True)
	state = db.Column(db.Integer)
	room = db.Column(db.String)
	relay = db.Column(db.String)
	date = db.Column(db.String)

	def __init__(self, state, room, relay):
		self.state = state
		self.room = room
		self.relay = relay
		self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class RelaysSchema(ma.Schema):
	class Meta:
		fields = ('id', 'state', 'room', 'relay', 'date')

class Pir(db.Model):
	__tablename__ = "pir"

	id = db.Column(db.Integer, primary_key=True)
	state = db.Column(db.Integer)
	room = db.Column(db.String)
	date = db.Column(db.String)

	def __init__(self, state, room):
		self.state = state
		self.room = room
		self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class PirSchema(ma.Schema):
	class Meta:
		fields = ('id', 'state', 'room', 'date')

class Pressure(db.Model):
	__tablename__ = "pressure"

	id = db.Column(db.Integer, primary_key=True)
	value = db.Column(db.Integer)
	room = db.Column(db.String)
	date = db.Column(db.String)

	def __init__(self, value, room):
		self.value = value
		self.room = room
		self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class PressureSchema(ma.Schema):
	class Meta:
		fields = ('id', 'value', 'room', 'date')

class UV(db.Model):
	__tablename__ = "uv"

	id = db.Column(db.Integer, primary_key=True)
	value = db.Column(db.Float)
	room = db.Column(db.String)
	date = db.Column(db.String)

	def __init__(self, value, room):
		self.value = value
		self.room = room
		self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class UVSchema(ma.Schema):
	class Meta:
		fields = ('id', 'value', 'room', 'date')

class Air25(db.Model):
	__tablename__ = "air25"

	id = db.Column(db.Integer, primary_key=True)
	value = db.Column(db.Integer)
	room = db.Column(db.String)
	date = db.Column(db.String)

	def __init__(self, value, room):
		self.value = value
		self.room = room
		self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class Air25Schema(ma.Schema):
	class Meta:
		fields = ('id', 'value', 'room', 'date')

class Air10(db.Model):
	__tablename__ = "air10"

	id = db.Column(db.Integer, primary_key=True)
	value = db.Column(db.Integer)
	room = db.Column(db.String)
	date = db.Column(db.String)

	def __init__(self, value, room):
		self.value = value
		self.room = room
		self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class Air10Schema(ma.Schema):
	class Meta:
		fields = ('id', 'value', 'room', 'date')

class Sky(db.Model):
	__tablename__ = "sky"

	id = db.Column(db.Integer, primary_key=True)
	value = db.Column(db.Float)
	room = db.Column(db.String)
	date = db.Column(db.String)

	def __init__(self, value, room):
		self.value = value
		self.room = room
		self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class SkySchema(ma.Schema):
	class Meta:
		fields = ('id', 'value', 'room', 'date')

class Rain(db.Model):
	__tablename__ = "rain"

	id = db.Column(db.Integer, primary_key=True)
	state = db.Column(db.Integer)
	room = db.Column(db.String)
	date = db.Column(db.String)

	def __init__(self, state, room, relay):
		self.state = state
		self.room = room
		self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class RainSchema(ma.Schema):
	class Meta:
		fields = ('id', 'state', 'room', 'date')

class Doorbell(db.Model):
	__tablename__ = "doorbell"

	id = db.Column(db.Integer, primary_key=True)
	state = db.Column(db.Integer)
	room = db.Column(db.String)
	date = db.Column(db.String)

	def __init__(self, state, room):
		self.state = state
		self.room = room
		self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class DoorbellSchema(ma.Schema):
	class Meta:
		fields = ('id', 'state', 'room', 'date')

class RGB(db.Model):
	__tablename__ = "rgb"

	id = db.Column(db.Integer, primary_key=True)
	red = db.Column(db.Integer)
	green = db.Column(db.Integer)
	blue = db.Column(db.Integer)
	room = db.Column(db.String)
	date = db.Column(db.String)

	def __init__(self, red, green, blue, room):
		self.red = red
		self.green = green
		self.blue = blue
		self.room = room
		self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class RGBSchema(ma.Schema):
	class Meta:
		fields = ('id', 'red', 'green', 'blue', 'room', 'date')

temperature_schemas = TemperatureSchema(many=True, strict=True)
humidity_schemas = HumiditySchema(many=True, strict=True)
luminosity_schemas = LuminositySchema(many=True, strict=True)
relays_schemas = RelaysSchema(many=True, strict=True)
pir_schemas = PirSchema(many=True, strict=True)
pressure_schemas = PressureSchema(many=True, strict=True)
uv_schemas = UVSchema(many=True, strict=True)
air25_schemas = Air25Schema(many=True, strict=True)
air10_schemas = Air10Schema(many=True, strict=True)
sky_schemas = SkySchema(many=True, strict=True)
rain_schemas = RainSchema(many=True, strict=True)
doorbell_schemas = DoorbellSchema(many=True, strict=True)
rgb_schemas = RGBSchema(many=True, strict=True)

def on_connect(client, userdata, flags, rc):
	for channel in channels:
		client.subscribe(channel)
		print('Subscribing to: {chan}'.format(chan=channel))
		# time.sleep(0.5)

# def on_message(client, userdata, message):
# 	message_r = message.payload.decode()
# 	print(message_r)
# 	data = {
# 		"value": float(message_r[:-1]),
# 		"room": message.topic
# 	}

# 	tables = {
# 		"T": Temperature,
# 		"H": Humidity,
# 		"L": Luminosity
# 	}

# 	new_row = tables[message_r[-1]](data['value'], data['room'])
# 	db.session.add(new_row)
# 	db.session.commit()

# 	print(f'Adding to DB: {message_r[-1]} with value ({ data["value"] }) and room ({ data["room"] })')
# 	try:
# 		new_data = get_data(message.topic[-1], message_r[-1], 1)
# 	except Exception as e:
# 		print(e)
# 	print(new_data)
# 	socketio.emit('get_data', new_data)

def _on_message(client, userdata, message):
	raw_topic = message.topic
	topic = "Room" + message.topic[-1]
	message = message.payload.decode()
	print(f'RECEIVED: {message}')

	new_row = None

	if message[1] == "R":
		split_message = message.split('R')
		data = {
			"id": topic[-1],
			"state": split_message[0],
			"relay": split_message[1],
			"room": topic
		}
		
		new_row = Relays(data['state'], data['room'], data['relay'])
		socketio.emit('relay_feedback', data)
	elif message[-1] == "P":
		data = {
			"state": message[0],
			"room": topic
		}

		new_row = Pir(data['state'], data['room'])
	elif message[-1] == "I":
		data = {
			"state": message[0],
			"room": topic
		}

		new_row = Rain(data['state'], data['room'])
	elif message[-1] == "D":
		data = {
			"state": message[0],
			"room": topic
		}

		new_row = Doorbell(data['state'], data['room'])

		if data['state'] == "1":
			print('SENDING DOORBELL NOTIFICATION')
			send_doorbell_notification()
	elif message[0] == "S":
		split_message = re.split(r'[A-Z]+', message)
		print(f"RECEIVED {split_message} from {topic}")
		print(split_message)
		data = {
			"id": topic[-1],
			"red": split_message[1],
			"green": split_message[2],
			"blue": split_message[3],
			"room": topic,
			"raw_room": raw_room
		}
		print(raw_topic.split('_'))
		if len(raw_topic.split('_')) == 1:
			new_row = RGB(data['red'], data['green'], data['blue'], data['room'])
			socketio.emit('rgb_feedback', data)

	else:
		data = {
			"value": float(message[:-1]),
			"room": topic
		}

		tables = {
			"T": Temperature,
			"H": Humidity,
			"L": Luminosity,
			"K": Pressure,
			"U": UV,
			"J": Air25,
			"F": Air10,
			"O": Sky
		}

		print(f'ROOM FOR {message[-1]}: {data["room"]}')

		new_row = tables[message[-1]](data['value'], data['room'])

	if new_row:
		db.session.add(new_row)
		db.session.commit()

		print(f"Adding to DB: {message}")
		new_data = None
		try:
			new_data = _get_data(data['room'][-1], list(filter(None, re.split(r'[^A-Z]+', message)))[0], 1)
			socketio.emit('get_data', new_data)
		except Exception as e:
			print(f'ERROR: {e}')

client.on_connect = on_connect
client.on_message = _on_message

# def get_data(room, dataset='ALL', limit=17):
# 	tables = {
# 		"T": (Temperature, temperature_schemas),
# 		"H": (Humidity, humidity_schemas),
# 		"L": (Luminosity, luminosity_schemas)
# 	}

# 	response = {
# 		"data": []
# 	}

# 	if dataset.upper() == 'ALL':
# 		for key, table in tables.items():
# 			foo = {
# 				"name": key,
# 				"id": room,
# 				"data": None,
# 				"labels": None,
# 			}

# 			foo['data'], foo['labels'] = retrive_single_data(room, key, tables, limit)
			
# 			response['data'].append(foo)
# 	else:
# 		foo = {
# 			"name": dataset.upper(),
# 			"id": room,
# 			"data": None,
# 			"labels": None,
# 		}

# 		foo['data'], foo['labels'] = retrive_single_data(room, dataset.upper(), tables, limit)
		
# 		response['data'].append(foo)


# 	return response

def _get_data(room, dataset='ALL', limit=17):
	tables = {
		"T": (Temperature, temperature_schemas),
		"H": (Humidity, humidity_schemas),
		"L": (Luminosity, luminosity_schemas),
		"R": (Relays, relays_schemas),
		"P": (Pir, pir_schemas),
		"K": (Pressure, pressure_schemas),
		"U": (UV, uv_schemas),
		"J": (Air25, air25_schemas),
		"F": (Air10, air10_schemas),
		"O": (Sky, sky_schemas),
		"I": (Rain, rain_schemas),
		"S": (RGB, rgb_schemas)
	}

	response = {
		"data": []
	}
	
	if dataset == 'ALL':
		dataset = ''.join(tables.keys())

	print(f'DATASET {dataset}')

	for key in dataset:
		print(f'GETTING DATA FOR: {key}')
		data = {
			"name": key,
			"id": room,
			"data": None,
			"labels": None
		}

		data['data'], data['labels'] = _retrive_single_data(room, key, tables[key][0], tables[key][1], limit)

		response['data'].append(data)

	print(f'response: {response}')
	return response

def _retrive_single_data(room, key, table, schema, limit):
	room = "Room" + room
	print(f"ROOM: {room}")
	data = []
	labels = None
	# if key == "R":
	# 	# print('RELAYS - RETRIVE SINGLE DATA')
	# 	data = [[], [], []]
	# 	labels = [[], [], []]
	# 	if result.data:
	# 		print('DUDEEEEEEEEEEEEEE RESULT DATA:')
	# 		print(result.data)
	# 		for row in result.data:
	# 			print(row)
	# 			data[int(row['relay'])].append(row['state'])
	# 			labels[int(row['relay'])].append(row['date'].split(' ')[1])
	# 			# if len(row_data) != 0:
	# 			# 	data.append(row_data)
	# 		data = [i[::-1] for i in data]
	# 		labels = [i[::-1] for i in labels]
	# 	# ODWROCIC TO CALE GOWNO
	# 	print('WE WILL BE SENDING THIS SHIT:')
	# 	print(data)
	# 	print(labels)
	if key == "R":
		data = [[], [], []]
		labels = [[], [], []] 

		if limit == 1:
			query = table.query.filter(table.room == room).order_by(table.id.desc()).limit(limit)
			result = schema.dump(query)
			if result.data:
					data[int(result.data[0]['relay'])] = [temp['state'] for temp in result.data][::-1]
					labels[int(result.data[0]['relay'])] = [temp['date'].split(' ')[1] for temp in result.data][::-1]
		else:
			NUMBER_OF_RELAYS = 3

			for relay in range(NUMBER_OF_RELAYS):
				query = table.query.filter(table.room == room).filter(table.relay == relay).order_by(table.id.desc()).limit(limit)
				result = schema.dump(query)
				if result.data:
					data[relay] = [temp['state'] for temp in result.data][::-1]
					labels[relay] = [temp['date'].split(' ')[1] for temp in result.data][::-1]
	else:
		print(table)
		query = table.query.filter(table.room == room).order_by(table.id.desc()).limit(limit)
		result = schema.dump(query)
		print(result)
		if result.data:
			if key == "P" or key == "I":
				data = [temp['state'] for temp in result.data][::-1]
			elif key == 'S':
				data = [[temp['red'], temp['green'], temp['blue']]for temp in result.data][::-1]
			else:
				data = [temp['value'] for temp in result.data][::-1]
			if not labels:
				labels = [temp['date'].split(' ')[1] for temp in result.data][::-1]

	print('WE WILL BE SENDING THIS SHIT:')
	print(data)
	print(labels)
	return (data, labels)

# def retrive_single_data(room, dataset, tables, limit):
# 	table = tables[dataset]

# 	query = table[0].query.filter(table[0].room == "Room" + room).order_by(table[0].id.desc()).limit(limit)
# 	result = table[1].dump(query)

# 	data = [temp['value'] for temp in result.data][::-1]
# 	labels = [temp['date'].split(' ')[1] for temp in result.data][::-1]

# 	return (data, labels)

@socketio.on('connect')
def handleConnect():
	print('User just got connected with id: ' + request.args.get('id'))
	data = _get_data(request.args.get('id'))
	emit('get_data', data)

@socketio.on('rgb')
def handleStrip(data):
	print(data)
	client.publish(topic=f"Room{data['id']}_{data['id']}", payload=data['message'])

@socketio.on('relay')
def handleRelay(data):
	print(data)
	client.publish(topic=f"Room{data['id']}_{data['id']}", payload=data['message'])

# !!!!!!!!!!!!!!!!!!!!!!!!
# USE WISELY
# db.drop_all()
# db.create_all()
# !!!!!!!!!!!!!!!!!!!!!!!!

# Run Server
if __name__ == '__main__':
	client.loop_start()
	socketio.run(app)