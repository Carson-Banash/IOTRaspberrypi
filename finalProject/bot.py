from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse
from gpiozero import LightSensor, MotionSensor, Button
from time import sleep
import I2C_LCD_Driver     
from paho.mqtt import client as mqtt
import ssl, re, os 
from json import dumps, loads

app = Flask(__name__)

path_to_root_cert = "/home/carson/Desktop/ITSC305/finalProject/certs/AmazonRootCA1.pem"                                 
path_to_device_cert = "/home/carson/Desktop/ITSC305/finalProject/certs/e3752fc4e17645d52aea0b341d96700518a40667497f4dd54c1ad2d7e9d27631-certificate.pem.crt"                                          
path_to_private_key = "/home/carson/Desktop/ITSC305/finalProject/certs/e3752fc4e17645d52aea0b341d96700518a40667497f4dd54c1ad2d7e9d27631-private.pem.key"
device_id = "Project_Sensor"
aws_url = "a3unv16yan389p-ats.iot.us-east-2.amazonaws.com" 
publish_topic = "light/control"
publish_qos = 1

def on_connect(client, userdata, flags, rc):
    print("Device connected with result code: " + str(rc))


def on_disconnect(client, userdata, rc):
    print("Device disconnected with result code: " + str(rc))


def on_publish(client, userdata, mid):
    print("Device message sent.")

def on_message(client, userdata, message):
    new_msg = loads(message.payload)
    print("Received Message:")
    print(new_msg)

def on_subscribe(client, userdata, mid, granted_qos):
    print("Client subscribed: ", str(mid), " with qos:", str(granted_qos))

def on_unsubscribe(client, userdata, mid):
    print("Client Unsubscribed")

def on_log(client, userdata, level, buf):
    print("Log:", str(buf))

def shut_down():
    print("System Exit initiated")
    awsClient.loop_stop()
    awsClient.disconnect()
    sleep(10)
    os._exit(0)

awsClient = mqtt.Client(client_id=device_id, protocol=mqtt.MQTTv311)

# MQTT callback functions
awsClient.on_connect = on_connect
awsClient.on_disconnect = on_disconnect
awsClient.on_publish = on_publish
awsClient.on_message = on_message
awsClient.on_subscribe = on_subscribe
awsClient.on_unsubscribe = on_unsubscribe

ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH,cafile=path_to_root_cert)
ssl_context.load_cert_chain(certfile=path_to_device_cert, keyfile=path_to_private_key)

# MQTT Client TLS settings. All certs and the key files are required (original way to create ssl context, if used, comment out two lines above)
#awsClient.tls_set(ca_certs=path_to_root_cert, certfile=path_to_device_cert, keyfile=path_to_private_key,
#cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)

awsClient.tls_set_context(context=ssl_context)
awsClient.tls_insecure_set(False)

# MQTT Client connect
awsClient.connect(aws_url, port=8883)
awsClient.loop_start()
sleep(5)

pir = MotionSensor(25)
ldr = LightSensor(19, charge_time_limit=0.09)

@app.route('/bot', methods=['POST'])

def bot():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()
    responded = False
    if 'status' in incoming_msg:
        intensity = ldr.value * 100

        if(intensity > 40):
            light = "On"
        else:
            light = "Off"

        if pir.is_active:
            movement = "Yes"
        else:
            movement = "No"

        string = """Current Status:
        Lights: {light}
        Movement: {movement}
        Last movement: N/A"""
        msg.body(string.format(light=light, movement=movement))
        # # return a quote
        # r = requests.get('https://api.quotable.io/random')
        # if r.status_code == 200:
        #     data = r.json()
        #     quote = f'{data["content"]} ({data["author"]})'
        # else:
        #     quote = 'I could not retrieve a quote at this time, sorry.'
        # msg.body(quote)
        responded = True
    if 'off' in incoming_msg:
        IoTmsg = dumps({'switch':1})   
        awsClient.publish(publish_topic, IoTmsg, qos=publish_qos)
        msg.body("Turning lights OFF!")
        responded = True
    if 'on' in incoming_msg:
        IoTmsg = dumps({'switch':0})   
        awsClient.publish(publish_topic, IoTmsg, qos=publish_qos)
        msg.body("Turning lights ON!")
        responded = True
    if not responded:
        msg.body('Options: STATUS, ON, OFF.')
    return str(resp)


if __name__ == '__main__':
    app.run(port=4000)