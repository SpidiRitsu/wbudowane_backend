import paho.mqtt.client as mqtt
import time
import random
import sys

broker_address = "spodo.pl"
broker_portno = 1883
client = mqtt.Client()
client.connect(broker_address, broker_portno)

topics_pub = {'A1': 'Room1', 'A2': 'Room2', 'E3': 'Room3'}
topics_sub = {'A1': 'Room1_1', 'A2': 'Room2_2', 'E3': 'Room3_3'}
channels = ['Room1', 'Room1_1', 'Room2', 'Room2_2', 'Room3', 'Room3_3']
A1 = {'B0': 0, 'B1': 0, 'B2': 0, 'R0': 0, 'R1': 0, 'R2': 0, 'S': 'S000R000G000B'}
A1_OLD = {'B0': 0, 'B1': 0, 'B2': 0, 'R0': 0, 'R1': 0, 'R2': 0, 'S': 'S000R000G000B'}
A2 = {'B0': 0, 'B1': 0, 'R0': 0, 'R1': 0, 'R2': 0, 'D': 0, 'S': 'S000R000G000B'}
A2_OLD = {'B0': 0, 'B1': 0, 'R0': 0, 'R1': 0, 'R2': 0, 'D': 0, 'S': 'S000R000G000B'}
E3 = {'B0': 0, 'B1': 0, 'B2': 0, 'R0': 0, 'R1': 0, 'R2': 0, 'S': 'S000R000G000B'}
E3_OLD = {'B0': 0, 'B1': 0, 'B2': 0, 'R0': 0, 'R1': 0, 'R2': 0, 'S': 'S000R000G000B'}

A1_temp = [22.00]
A1_hum = [48.20]
A1_lum = [500]

A2_temp = [25.00]
A2_hum = [30.20]
A2_lum = [250]

E3_temp = [21.00]
E3_hum = [60.20]
E3_lum = [1000]

choices = []


def menu():
    user_input = input('Do you want to simulate Arduino (A1)\n1. yes\n2. no\nInput: ')
    if user_input == '1':
        user_input = input('Do you want to simulate DHT22 \n1. YES\n2. NO\nInput: ')
        if user_input == '1':
            choices.append(11)
        user_input = input('Do you want to simulate TSL \n1. YES\n2. NO\nInput: ')
        if user_input == '1':
            choices.append(12)
        user_input = input('Do you want to use Buttons and Relays \n1. YES\n2. NO\nInput: ')
        if user_input == '1':
            choices.append(13)
    user_input = input('Do you want to simulate Arduino (A2)\n1. yes\n2. no\nInput: ')
    if user_input == '1':
        user_input = input('Do you want to simulate DHT22 \n1. YES\n2. NO\nInput: ')
        if user_input == '1':
            choices.append(21)
        user_input = input('Do you want to simulate TSL \n1. YES\n2. NO\nInput: ')
        if user_input == '1':
            choices.append(22)
        user_input = input('Do you want to use Buttons and Relays \n1. YES\n2. NO\nInput: ')
        if user_input == '1':
            choices.append(23)
    user_input = input('Do you want to simulate ESP (E3)\n1. yes\n2. no\nInput: ')
    if user_input == '1':
        user_input = input('Do you want to simulate DHT22 \n1. YES\n2. NO\nInput: ')
        if user_input == '1':
            choices.append(31)
        user_input = input('Do you want to simulate TSL \n1. YES\n2. NO\nInput: ')
        if user_input == '1':
            choices.append(32)
        user_input = input('Do you want to use Buttons and Relays \n1. YES\n2. NO\nInput: ')
        if user_input == '1':
            choices.append(33)


if len(sys.argv) > 1:
    tmp = sys.argv[1:]
    for i in tmp:
        choices.append(int(i))
else:
    menu()
print(choices)


def on_connect(client, userdata, flags, rc):
    for channel in channels:
        client.subscribe(channel)
        print('Subscribing to: {chan}'.format(chan=channel))
        time.sleep(0.5)


def on_message_R_11(client, userdata, message):
    if 13 in choices:
        global A1_OLD
        received_msg = message.payload.decode()
        print('received', received_msg, 'from:', message.topic)
        if received_msg[0] == '$':
            return
        elif received_msg == '00':
            A1['R0'] = 0
        elif received_msg == '01':
            A1['R0'] = 1
        elif received_msg == '10':
            A1['R1'] = 0
        elif received_msg == '11':
            A1['R1'] = 1
        elif received_msg == '20':
            A1['R2'] = 0
        elif received_msg == '21':
            A1['R2'] = 1
        elif received_msg[0] == 'S':
            A1['S'] = received_msg[1:]
            client.publish(topic='Room1', payload=A1['S'])
            return
        for k, v in A1.items():
            if A1[k] != A1_OLD[k]:
                client.publish(topic='Room1', payload='{value}{key}'.format(value=v, key=k))
                A1_OLD[k] = A1[k]
        print(A1)


def on_message_R_22(client, userdata, message):
    if 23 in choices:
        global A2_OLD
        received_msg = message.payload.decode()
        print('received', received_msg, 'from:', message.topic)
        if received_msg[0] == '$':
            return
        elif received_msg == '00':
            A2['R0'] = 0
        elif received_msg == '01':
            A2['R0'] = 1
        elif received_msg == '10':
            A2['R1'] = 0
        elif received_msg == '11':
            A2['R1'] = 1
        elif received_msg == '20':
            A2['R2'] = 0
        elif received_msg == '21':
            A2['R2'] = 1
        elif received_msg[0] == 'S':
            A2['S'] = received_msg[1:]
            client.publish(topic='Room2', payload=A2['S'])
            return
        for k, v in A2.items():
            if A2[k] != A2_OLD[k]:
                client.publish(topic='Room2', payload='{value}{key}'.format(value=v, key=k))
                A2_OLD[k] = A2[k]
        print(A2)


def on_message_R_33(client, userdata, message):
    if 33 in choices:
        global E3_OLD
        received_msg = message.payload.decode()
        print('received', received_msg, 'from:', message.topic)
        if received_msg[0] == '$':
            return
        elif received_msg == '00':
            E3['R0'] = 0
        elif received_msg == '01':
            E3['R0'] = 1
        elif received_msg == '10':
            E3['R1'] = 0
        elif received_msg == '11':
            E3['R1'] = 1
        elif received_msg == '20':
            E3['R2'] = 0
        elif received_msg == '21':
            E3['R2'] = 1
        elif received_msg[0] == 'S':
            E3['S'] = received_msg[1:]
            client.publish(topic='Room3', payload=E3['S'])
            return
        for k, v in A1.items():
            if E3[k] != E3_OLD[k]:
                client.publish(topic='Room3', payload='{value}{key}'.format(value=v, key=k))
                E3_OLD[k] = E3[k]
        print(E3)


client.on_connect = on_connect
client.message_callback_add('Room1_1', on_message_R_11)
client.message_callback_add('Room2_2', on_message_R_22)
client.message_callback_add('Room3_3', on_message_R_33)

A1_sens = 30
A1_last = 0
A2_sens = 30
A2_last = 0
E3_sens = 30
E3_last = 0
lucky = [1, 2, 3, 0.5, 0.2, 3, 4, 1, 0.4, 1.5, 2.5, 0, 1, 2]

while True:
    client.loop()
    t1 = time.time()
    if t1 - A1_last > A1_sens:
        A1_last = time.time()
        if random.randint(0, 1) == 1:
            temp = A1_temp[-1] + 0.5 * lucky[random.randint(0, len(lucky) - 1)]
            A1_temp.append(temp)
        else:
            temp = A1_temp[-1] - 0.5 * lucky[random.randint(0, len(lucky) - 1)]
            A1_temp.append(temp)
        if random.randint(0, 1) == 1:
            hum = A1_hum[-1] + 0.5 * lucky[random.randint(0, len(lucky) - 1)]
            A1_hum.append(hum)
        else:
            hum = A1_hum[-1] - 0.5 * lucky[random.randint(0, len(lucky) - 1)]
            A1_hum.append(hum)
        if random.randint(0, 1) == 1:
            lux = A1_lum[-1] + 10 * lucky[random.randint(0, len(lucky) - 1)]
            A1_lum.append(lux)
        else:
            lux = A1_lum[-1] - 10 * lucky[random.randint(0, len(lucky) - 1)]
            A1_lum.append(lux)
        if hum < 0:
            hum = hum * (-1)
        if lux < 0:
            lux = lux * (-1)
        output = ''
        if 11 in choices:
            print('Sending temp:', temp, 'hum:', hum)
            client.publish(topic='Room1', payload=str(round(temp, 2)) + 'T')
            client.publish(topic='Room1', payload=str(round(hum, 2)) + 'H')
        if 12 in choices:
            if 11 in choices:
                print('Sending lux:', lux)
                client.publish(topic='Room1', payload=str(round(lux, 2)) + 'L')
    if t1 - A2_last > A1_sens:
        A2_last = time.time()
        if random.randint(0, 1) == 1:
            temp = A2_temp[-1] + 0.5 * lucky[random.randint(0, len(lucky) - 1)]
            A2_temp.append(temp)
        else:
            temp = A2_temp[-1] - 0.5 * lucky[random.randint(0, len(lucky) - 1)]
            A2_temp.append(temp)
        if random.randint(0, 1) == 1:
            hum = A2_hum[-1] + 0.5 * lucky[random.randint(0, len(lucky) - 1)]
            A2_hum.append(hum)
        else:
            hum = A2_hum[-1] - 0.5 * lucky[random.randint(0, len(lucky) - 1)]
            A2_hum.append(hum)
        if random.randint(0, 1) == 1:
            lux = A2_lum[-1] + 10 * lucky[random.randint(0, len(lucky) - 1)]
            A2_lum.append(lux)
        else:
            lux = A2_lum[-1] - 10 * lucky[random.randint(0, len(lucky) - 1)]
            A2_lum.append(lux)
        if hum < 0:
            hum = hum * (-1)
        if lux < 0:
            lux = lux * (-1)
        output = ''
        if 21 in choices:
            print('Sending temp:', temp, 'hum:', hum)
            client.publish(topic='Room2', payload=str(round(temp, 2)) + 'T')
            client.publish(topic='Room2', payload=str(round(hum, 2)) + 'H')
        if 22 in choices:
            if 21 in choices:
                print('Sending lux:', lux)
                client.publish(topic='Room1', payload=str(round(lux, 2)) + 'L')
    if t1 - E3_last > A1_sens:
        E3_last = time.time()
        if random.randint(0, 1) == 1:
            temp = E3_temp[-1] + 0.5 * lucky[random.randint(0, len(lucky) - 1)]
            E3_temp.append(temp)
        else:
            temp = E3_temp[-1] - 0.5 * lucky[random.randint(0, len(lucky) - 1)]
            E3_temp.append(temp)
        if random.randint(0, 1) == 1:
            hum = E3_hum[-1] + 0.5 * lucky[random.randint(0, len(lucky) - 1)]
            E3_hum.append(hum)
        else:
            hum = E3_hum[-1] - 0.5 * lucky[random.randint(0, len(lucky) - 1)]
            E3_hum.append(hum)
        if random.randint(0, 1) == 1:
            lux = E3_lum[-1] + 10 * lucky[random.randint(0, len(lucky) - 1)]
            E3_lum.append(lux)
        else:
            lux = E3_lum[-1] - 10 * lucky[random.randint(0, len(lucky) - 1)]
            E3_lum.append(lux)
        if hum < 0:
            hum = hum * (-1)
        if lux < 0:
            lux = lux * (-1)
        output = ''
        if 31 in choices:
            print('Sending temp:', temp, 'hum:', hum)
            client.publish(topic='Room3', payload=str(round(temp, 2)) + 'T')
            client.publish(topic='Room3', payload=str(round(hum, 2)) + 'H')
        if 32 in choices:
            print('Sending lux:', lux)
            client.publish(topic='Room1', payload=str(round(lux, 2)) + 'L')
    if len(A1_temp) > 100:
        A1_temp = A1_temp[80:]
        A1_hum = A1_hum[80:]
        A1_lum = A1_lum[80:]

        A2_temp = A2_temp[80:]
        A2_hum = A2_hum[80:]
        A2_lum = A2_lum[80:]

        E3_temp = E3_temp[80:]
        E3_hum = E3_hum[80:]
        E3_lum = E3_lum[80:]