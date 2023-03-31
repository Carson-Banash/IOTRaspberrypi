#! /usr/bin/env python3

# Created by Lubos Kuzma, SADT, SAIT
# October, 2022
# Program sends random integers to AWS IoT Core
# You can shut down the program by pubishing message "command":"exit" to the topic "back/msgs". this is done from AWS IoT Core


from time import sleep
import os                                         # os for shutdown command
from random import randint                        # randint for generating random #s
from json import dumps, loads                     # JSON manipulation. Not necessary, but makes data more readable

from awscrt import io, http, auth, mqtt
from awsiot import mqtt_connection_builder

from cryptoauthlib import *
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

import cert_definitions

ATCA_SUCCESS = 0x00

#IoT settings
pkcs11_token = "00ABC"
user_pin = "1234"
pkcs11_lib_path = "/usr/lib/libcryptoauth.so"
pkcs11_device_cert = "/home/carson/Desktop/ITSC305/lab5/device.crt"
pkcs11_signer_cert = "/home/carson/Desktop/ITSC305/lab5/signer-ca.crt"

device_id = "lab6_pi"
aws_url = "a1ryb83dujtssq-ats.iot.us-east-2.amazonaws.com"  # taken from AWS IoT Core
mqtt_port = 8883
mqtt_connected = False

publish_topic = "lab6/messages"
publish_qos = 1
subscribe_topic = "back/msgs"
subscribe_qos = 1

def shut_down():
    print("System Exit initiated")
    mqtt_connection.disconnect()
    sleep(5)
    os._exit(0)

def build_pkcs11_mqtt_connection(on_connection_interrupted, on_connection_resumed):
    global device_id, pkcs11_token, pkcs11_slot_id, pkcs11_lib, \
            pkcs11_device_cert, pkcs11_signer_cert, aws_url,    \
            mqtt_port, user_pin

    print(f"Loading PKCS#11 library '{pkcs11_lib_path}' ...")
    pkcs11_lib = io.Pkcs11Lib(
        file=pkcs11_lib_path,
        behavior=io.Pkcs11Lib.InitializeFinalizeBehavior.STRICT)
    print("Loaded!")
    
    # Create MQTT connection
    mqtt_connection = mqtt_connection_builder.mtls_with_pkcs11(
        pkcs11_lib=pkcs11_lib,
        user_pin=user_pin,
        token_label=pkcs11_token,
        cert_bytes=pkcs11_device_cert,
        #ca_bytes=pkcs11_signer_cert,     
        endpoint=aws_url,
        port=mqtt_port,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        client_id=device_id,
        clean_session=True,
        keep_alive_secs=30,
        enable_metrics_collection=False
       )
    return mqtt_connection

# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))
    mqtt_connected = False
    awsConnection = mqtt_connection.connect()

# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))
    mqtt_connected = True

def on_message(topic, payload, dup, qos, retain, **kwargs):
    print("Message received. Topic:", topic, "qos:", qos, "payload:", payload)
    new_msg = loads(payload)
    # shutdown if the ommand from the AWS command is "command":"exit"
    # TODO: this should be rewritten in separate function
    if ('command','exit') in new_msg.items():
        shut_down()


def load_pkcs11_certs():
    global pkcs11_device_cert, pkcs11_signer_cert
    
    cfg = cfg_ateccx08a_i2c_default()
    # Set the i2c bus
    cfg.cfg.atcai2c.bus = 1
    cfg.cfg.atcai2c.address = 0x6A #(6C)
    # Initialize the stack
    assert atcab_init(cfg) == ATCA_SUCCESS
    print('')
    #pkcs11_signer_cert = read_signer_cert()
    pkcs11_device_cert = read_device_cert()
    # Free the library
    atcab_release()

def read_signer_cert():
    cert = bytearray(1024)
    cert_len = AtcaReference(len(cert))
    assert ATCA_SUCCESS == atcacert_read_cert(cert_definitions.signer_cert_def, bytearray(), cert, cert_len)
    signer = x509.load_der_x509_certificate(cert, default_backend())
    return signer.public_bytes(encoding=serialization.Encoding.PEM)

def read_device_cert():
    public_key = bytearray(64)
    assert ATCA_SUCCESS == atcab_read_pubkey(cert_definitions.signer_cert_def.public_key_dev_loc.slot, public_key)
    cert = bytearray(1024)
    cert_len = AtcaReference(len(cert))
    assert Status.ATCA_SUCCESS == atcacert_read_cert(cert_definitions.device_cert_def, public_key, cert, cert_len)
    device = x509.load_der_x509_certificate(cert, default_backend())
    return device.public_bytes(encoding=serialization.Encoding.PEM)

# Load certificate
load_pkcs11_certs()

# AWS mqtt
mqtt_connection = build_pkcs11_mqtt_connection(on_connection_interrupted, on_connection_resumed)
awsConnection = mqtt_connection.connect()
connect_res = awsConnection.result()
if ('session_present') in connect_res.keys():
    mqtt_connected = True
    print("Connected.")
    print("Existing session:", connect_res["session_present"])
else:
    print("Error connecting: ", connect_res)
    shut_down()

mqtt_connection.subscribe(topic=subscribe_topic, qos=mqtt.QoS.AT_LEAST_ONCE, callback=on_message)


# Loop
while True:
    try:
        sleep(10)
        IoTmsg = dumps({'voltage':str(randint(0,10))})               # creating dictionary {"voltage":"random integer"} and packing it into JSON format
        if mqtt_connected:
            mqtt_connection.publish(topic=publish_topic, payload=IoTmsg, qos=mqtt.QoS.AT_LEAST_ONCE)    # publishing to topic
            print('published ',IoTmsg, publish_topic, publish_qos)
    except KeyboardInterrupt:
        shut_down()
        break

