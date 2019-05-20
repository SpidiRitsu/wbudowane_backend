from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import paho.mqtt.client as mqtt
import datetime
import os

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)
# MQTT
broker_address = "spodo.pl"
broker_portno = 1883
client = mqtt.Client()
client.connect(broker_address, broker_portno)

channels = ['Room1_1', 'Room2_2', 'Room3_3']
def on_connect(client, userdata, flags, rc):
	for channel in channels:
		client.subscribe(channel)
		print('Subscribing to: {chan}'.format(chan=channel))
		time.sleep(0.5)

client.on_connect = on_connect

# Models and Schemes
class Temperature(db.Model):
	__tablename__ = "temperature"

	id = db.Column(db.Integer, primary_key=True)
	value = db.Column(db.Float)
	room = db.Column(db.String)
	date = db.Column(db.DateTime)

	def __init__(self, value, room):
		self.value = value
		self.room = room
		self.date = datetime.datetime.now()

class TemperatureSchema(ma.Schema):
	class Meta:
		fields = ('id', 'value', 'room', 'date')

class Humidity(db.Model):
	__tablename__ = "humidity"

	id = db.Column(db.Integer, primary_key=True)
	value = db.Column(db.Float)
	room = db.Column(db.String)
	date = db.Column(db.DateTime)

	def __init__(self, value, room):
		self.value = value
		self.room = room
		self.date = datetime.datetime.now()

class HumiditySchema(ma.Schema):
	class Meta:
		fields = ('id', 'value', 'room', 'date')

class Luminosity(db.Model):
	__tablename__ = "luminosity"

	id = db.Column(db.Integer, primary_key=True)
	value = db.Column(db.Float)
	room = db.Column(db.String)
	date = db.Column(db.DateTime)

	def __init__(self, value, room):
		self.value = value
		self.room = room
		self.date = datetime.datetime.now()

class LuminositySchema(ma.Schema):
	class Meta:
		fields = ('id', 'value', 'room', 'date')

temperature_schema = TemperatureSchema(strict=True)
temperature_schemas = TemperatureSchema(many=True, strict=True)
humidity_schema = HumiditySchema(strict=True)
humidity_schemas = HumiditySchema(many=True, strict=True)
luminosity_schema = LuminositySchema(strict=True)
luminosity_schemas = LuminositySchema(many=True, strict=True)

# !!!!!!!!!!!!!!!!!!!!!!!!
# USE WISELY
# db.drop_all()
# db.create_all()
# !!!!!!!!!!!!!!!!!!!!!!!!

# POSTS
@app.route('/temperature', methods=['POST'])
def add_temperature():
	print(request.json)
	value = request.json['value']
	room = request.json['room']

	new_temperature = Temperature(value, room)

	db.session.add(new_temperature)
	db.session.commit()

	return temperature_schema.jsonify(new_temperature)

@app.route('/humidity', methods=['POST'])
def add_humidity():
	print(request.json)
	value = request.json['value']
	room = request.json['room']

	new_humidity = Humidity(value, room)

	db.session.add(new_humidity)
	db.session.commit()

	return humidity_schema.jsonify(new_humidity)

@app.route('/luminosity', methods=['POST'])
def add_luminosity():
	print(request.json)
	value = request.json['value']
	room = request.json['room']

	new_luminosity = Luminosity(value, room)

	db.session.add(new_luminosity)
	db.session.commit()

	return luminosity_schema.jsonify(new_luminosity)

# GETS
@app.route('/get_temperature', methods=['GET'])
def get_temperature():
	temperature = Temperature.query.all()
	result = temperature_schemas.dump(temperature)
	return jsonify(result.data)

@app.route('/get_humidity', methods=['GET'])
def get_humidity():
	humidity = Humidity.query.all()
	result = humidity_schemas.dump(humidity)
	return jsonify(result.data)

@app.route('/get_luminosity', methods=['GET'])
def get_luminosity():
	luminosity = Luminosity.query.all()
	result = luminosity_schemas.dump(luminosity)
	return jsonify(result.data)

# RELAYS
@app.route('/relay/<room>/<relay>/<state>', methods=['GET'])
def change_relay(room, relay, state):
	client.publish(topic=f"Room{room}_{room}", payload=f"{relay}{state}", qos=1, retain=False)
	return 'Working'

# RGB
@app.route('/rgb/<room>/<red>/<green>/<blue>', methods=['GET'])
def change_rgb(room, red, green, blue):
	client.publish(topic=f"Room{room}_{room}", payload=f"S{red.zfill(3)}R{green.zfill(3)}G{blue.zfill(3)}B", qos=1, retain=False)
	return 'Working'

# Run Server
if __name__ == '__main__':
	app.run(debug=True)