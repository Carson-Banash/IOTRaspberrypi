from time import sleep
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory         
from paho.mqtt import client as mqtt
import ssl, re, os 
from json import dumps, loads   

factory = PiGPIOFactory()
servo = Servo(12, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory)


path_to_root_cert = "/home/carson/Desktop/ITSC305/finalProject/switch/AmazonRootCA1.pem"                                 
path_to_device_cert = "/home/carson/Desktop/ITSC305/finalProject/switch/7ebdba88a3bb3b8dadf9221122badef84be7c890b1bb5b565abdd8e6b31b69ce-certificate.pem.crt"
path_to_private_key = "/home/carson/Desktop/ITSC305/finalProject/switch/7ebdba88a3bb3b8dadf9221122badef84be7c890b1bb5b565abdd8e6b31b69ce-private.pem.key"
device_id = "Project_Switch"
aws_url = "a3unv16yan389p-ats.iot.us-east-2.amazonaws.com"  

subscribe_topic = "light/control"
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
    # # shutdown if the ommand from the AWS command is "command":"exit"
    # # TODO: this should be rewritten in separate function
    # if ('command','exit') in new_msg.items():
    #     shut_down()
    if new_msg['switch'] == 1:
        servo.max()
    else:
        servo.min()


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
    servo.close()
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
            # publishing to topic

    except KeyboardInterrupt:
        shut_down()
        break
        exit()