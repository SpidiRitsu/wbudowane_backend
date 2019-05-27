from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
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
		socketio.emit('get_data', data)
	except Exception as e:
		print(e)
	print('SENDING')

client.on_connect = on_connect
client.on_message = on_message

@socketio.on('connect')
def handleConnect():
	print('User just got connected!')
	data = {
		"x": 200,
		"y": 200,
		"value": 69
	}
	emit('get_data', data)


@socketio.on('message')
def handleMessage(msg):
	print('Message: ' + msg)

# TEMP
from flask_marshmallow import Marshmallow
ma = Marshmallow(app)
class TemperatureSchema(ma.Schema):
	class Meta:
		fields = ('id', 'value', 'room', 'date')
class HumiditySchema(ma.Schema):
	class Meta:
		fields = ('id', 'value', 'room', 'date')
class LuminositySchema(ma.Schema):
	class Meta:
		fields = ('id', 'value', 'room', 'date')
temperature_schema = TemperatureSchema(strict=True)
temperature_schemas = TemperatureSchema(many=True, strict=True)
humidity_schema = HumiditySchema(strict=True)
humidity_schemas = HumiditySchema(many=True, strict=True)
luminosity_schema = LuminositySchema(strict=True)
luminosity_schemas = LuminositySchema(many=True, strict=True)

# GETS
@app.route('/get_temperature', methods=['GET'])
def get_temperature():
	params = request.query_string.decode().split('=')
	params = dict(zip(*[iter(params)]*2))
	if params and (params['room'] == "1" or params['room'] == "2" or params['room'] == "3"):
		temperature = Temperature.query.filter(Temperature.room == f"Room{params['room']}").order_by(Temperature.id.desc()).limit(10)
	else:
		temperature = Temperature.query.order_by(Temperature.id.desc()).limit(10)
	result = temperature_schemas.dump(temperature)
	data = {
		"date": [temp['date'].split(' ')[1] for temp in result.data][::-1],
		"value": [temp['value'] for temp in result.data][::-1]
	}
	return json.dumps(data);

@app.route('/get_humidity', methods=['GET'])
def get_humidity():
	params = request.query_string.decode().split('=')
	params = dict(zip(*[iter(params)]*2))
	if params and (params['room'] == "1" or params['room'] == "2" or params['room'] == "3"):
		humidity = Humidity.query.filter(Humidity.room == f"Room{params['room']}").order_by(Humidity.id.desc()).limit(10)
	else:
		humidity = Humidity.query.order_by(Humidity.id.desc()).limit(10)
	result = humidity_schemas.dump(humidity)
	print(result)
	# return jsonify(result.data)
	data = {
		"date": [temp['date'].split(' ')[1] for temp in result.data][::-1],
		"value": [temp['value'] for temp in result.data][::-1]
	}
	return json.dumps(data);

@app.route('/get_luminosity', methods=['GET'])
def get_luminosity():
	params = request.query_string.decode().split('=')
	params = dict(zip(*[iter(params)]*2))
	if params and (params['room'] == "1" or params['room'] == "2" or params['room'] == "3"):
		luminosity = Luminosity.query.filter(Luminosity.room == f"Room{params['room']}").order_by(Luminosity.id.desc()).limit(10)
	else:
		luminosity = Luminosity.query.order_by(Luminosity.id.desc()).limit(10)
	result = luminosity_schemas.dump(luminosity)
	# return jsonify(result.data)
	data = {
		"date": [temp['date'].split(' ')[1] for temp in result.data][::-1],
		"value": [temp['value'] for temp in result.data][::-1]
	}
	return json.dumps(data);

# Run Server
if __name__ == '__main__':
	client.loop_start()
	socketio.run(app)