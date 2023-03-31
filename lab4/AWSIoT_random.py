#! /usr/bin/env python3

# Created by Lubos Kuzma, SADT, SAIT
# May, 2022
# Program sends random integers to AWS IoT Core
# You can shut down the program by pubishing message "command":"exit" to the topic "back/msgs". this is done from AWS IoT Core


from time import sleep, process_time            #process_time is used for delays. Counts the running time of process
from paho.mqtt import client as mqtt
import ssl, re, os                              #SSL, RegEx, os for shutdown command
from random import randint                      #randint for generating random #s
from json import dumps, loads                   #JSON manipulation. Not necessary, but makes data more readable

#IoT settings

path_to_root_cert = "./certs/root-CA.crt"                                  # local path to Amazon Root Cetificate
path_to_device_cert = "./certs/raspberry_pi_carson.cert.pem"                                # local path to Device certificate pem or crt            
path_to_private_key = "./certs/raspberry_pi_carson.private.key"                                # local path to Private key
device_id = "raspberry_pi_carson"
aws_url = "a1ryb83dujtssq-ats.iot.us-east-2.amazonaws.com"                                            # taken from AWS IoT Core

publish_topic = "temp/reading"
publish_qos = 1
subscribe_topic = "back/msgs"
subscribe_qos = 1


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
    # shutdown if the ommand from the AWS command is "command":"exit"
    # TODO: this should be rewritten in separate function
    if ('command','exit') in new_msg.items():
        shut_down()

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

# MQTT Client definition
awsClient = mqtt.Client(client_id=device_id, protocol=mqtt.MQTTv311)

# MQTT callback functions
awsClient.on_connect = on_connect
awsClient.on_disconnect = on_disconnect
awsClient.on_publish = on_publish
awsClient.on_message = on_message
awsClient.on_subscribe = on_subscribe
awsClient.on_unsubscribe = on_unsubscribe
#awsClient.on_log = on_log                                             # uncomment for logging

# create ssl context and settings
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
awsClient.subscribe((subscribe_topic, subscribe_qos))

# Loop
while True:
    try:

        sleep(10)
        IoTmsg = dumps({'voltage':str(randint(0,10))})               # creating dictionary {"voltage":"random integer"} and packing it into JSON format
        awsClient.publish(publish_topic, IoTmsg, qos=publish_qos)    # publishing to topic

    except KeyboardInterrupt:
        shut_down()
        break
        exit()

