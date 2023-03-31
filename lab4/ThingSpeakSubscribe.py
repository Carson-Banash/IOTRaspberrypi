"""
Written by Lubos Kuzma
March 2021

Example of MQTT protocol Subscribe function
This example uses MQTT v3.11 to subscribe to "Field 5" topic of my private ThingSpeak Channel
Use this example as a template for Lab 5 and/or the final Project

For this to work, you need to instal paho-mqtt library:
sudo pip3 install paho-mqtt

https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php

""" 

from time import sleep
import paho.mqtt.client as mqtt

MQTT_CLIENT_ID = "TestThingspeakID" # This is for your own client identification. Can be anything
MQTT_USERNAME = "mwa0000021466240" #This is the ThingsSpeak's Author
MQTT_PASSWD = "9DM50MKH45RPGMRA" #This is the MQTT API Key found under My Profile in ThingSpeak
MQTT_HOST = "mqtt.thingspeak.com" #This is the ThingSpeak hostname
MQTT_PORT = 1883 #Typical port # for MQTT protocol. If using TLS -> 8883
CHANNEL_ID = "1308394" #Channel ID found on ThingSpeak website
MQTT_READ_APIKEY = "YLEWJIRNAAZ3T04G" # Read API Key found under ThingSpeak Channel Settings
MQTT_SUBSCRIBE_TOPIC = "channels/" + CHANNEL_ID + "/subscribe/fields/field5/" + MQTT_READ_APIKEY

""" 
Standard callback functions. See Phao MQTT documentation for more
This will be called on receipt of a message from the subscribed topic(s)
"""

def on_message(client, userdata, message):
    print("Message topic: ", message.topic)    
    print("Message payload: ", message.payload)
    print("Message QoS: ", message.qos)

""" 
This function will be called upon connection
"""

def on_connect(client, userdata, flags, rc):
    print("Connected ", rc)

""" 
This function is used for logging. For this to work, you must uncomment the callback binding
"""

def on_log(client, userdata, level, buf):
    print("log:", buf)

try:
    """ create client instance"""
    client = mqtt.Client(client_id=MQTT_CLIENT_ID, clean_session=True, userdata=None, protocol=mqtt.MQTTv311, transport="tcp")
    
    """ standard callback bindings """

    client.on_connect = on_connect
    client.on_message = on_message
    #client.on_subscribe = on_subscribe
    #client.on_unsubscribe = on_unsubscribe
    #client.on_disconnect = on_disconnect
    #client.on_publish = on_publish
    #client.on_log = on_log

    """ Set the conneciton authentication. """
    client.username_pw_set(MQTT_USERNAME, password=MQTT_PASSWD)
    """ Connect client """
    client.connect(MQTT_HOST, port=MQTT_PORT, keepalive=60)
    """ start the looping of client connection. This needs to be done otherwise the connection will only happen once and expire """
    client.loop_start()

    """ 
    subscribe to the predefined topic(s). To subscribe to multiple topics, define a List of Tuples:
    client.subscribe([(topic1, qos),(topic2, qos),...])
    """
    client.subscribe(MQTT_SUBSCRIBE_TOPIC, qos=0)
    
    while True:
        sleep(1)
        if not client.is_connected:
            print("Client disconnected. Trying to reconnect.")
            client.reconnect()

except KeyboardInterrupt:
    client.unsubscribe(MQTT_SUBSCRIBE_TOPIC)
    client.disconnect()