from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_socketio import SocketIO, send, emit
import paho.mqtt.client as mqtt
import datetime
import os
import json

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

channels = ['Room1', 'Room1_1', 'Room2', 'Room2_2', 'Room3', 'Room3_3']

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

temperature_schema = TemperatureSchema(strict=True)
temperature_schemas = TemperatureSchema(many=True, strict=True)
humidity_schema = HumiditySchema(strict=True)
humidity_schemas = HumiditySchema(many=True, strict=True)
luminosity_schema = LuminositySchema(strict=True)
luminosity_schemas = LuminositySchema(many=True, strict=True)

def on_connect(client, userdata, flags, rc):
	for channel in channels:
		client.subscribe(channel)
		print('Subscribing to: {chan}'.format(chan=channel))
		# time.sleep(0.5)

def on_message(client, userdata, message):
	message_r = message.payload.decode()
	data = {
		"value": float(message_r[:-1]),
		"room": message.topic
	}

	tables = {
		"T": Temperature,
		"H": Humidity,
		"L": Luminosity
	}

	new_row = tables[message_r[-1]](data['value'], data['room'])
	db.session.add(new_row)
	db.session.commit()

	print(f'Adding to DB: {message_r[-1]} with value ({ data["value"] }) and room ({ data["room"] })')
	try:
		new_data = get_data(message.topic[-1], message_r[-1], 1)
	except Exception as e:
		print(e)
	print(new_data)
	socketio.emit('get_data', new_data)

client.on_connect = on_connect
client.on_message = on_message

def get_data(room, dataset='ALL', limit=10):
	tables = {
		"T": (Temperature, temperature_schemas),
		"H": (Humidity, humidity_schemas),
		"L": (Luminosity, luminosity_schemas)
	}

	response = {
		"data": []
	}

	if dataset.upper() == 'ALL':
		for key, table in tables.items():
			foo = {
				"name": key,
				"id": room,
				"data": None,
				"labels": None,
			}

			foo['data'], foo['labels'] = retrive_single_data(room, key, tables, limit)
			
			response['data'].append(foo)
	else:
		foo = {
			"name": dataset.upper(),
			"id": room,
			"data": None,
			"labels": None,
		}

		foo['data'], foo['labels'] = retrive_single_data(room, dataset.upper(), tables, limit)
		
		response['data'].append(foo)


	return response

def retrive_single_data(room, dataset, tables, limit):
	table = tables[dataset]

	query = table[0].query.filter(table[0].room == "Room" + room).order_by(table[0].id.desc()).limit(limit)
	result = table[1].dump(query)

	data = [temp['value'] for temp in result.data][::-1]
	labels = [temp['date'].split(' ')[1] for temp in result.data][::-1]

	return (data, labels)

@socketio.on('connect')
def handleConnect():
	print('User just got connected with id: ' + request.args.get('id'))
	data = get_data(request.args.get('id'))
	emit('get_data', data)


@socketio.on('message')
def handleMessage(msg):
	print('Message: ' + msg)

# Run Server
if __name__ == '__main__':
	client.loop_start()
	socketio.run(app)