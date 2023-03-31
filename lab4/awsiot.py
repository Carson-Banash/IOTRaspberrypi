import RPi.GPIO as GPIO
import dht11_library as dht11
import smbus
from gpiozero import Button
import I2C_LCD_Driver
from time import sleep

from time import process_time            
from paho.mqtt import client as mqtt
import ssl, re, os                                              
from json import dumps, loads

#aws code
path_to_root_cert = "./certs/root-CA.crt"                                  # local path to Amazon Root Cetificate
path_to_device_cert = "./certs/raspberry_pi_carson.cert.pem"                                # local path to Device certificate pem or crt            
path_to_private_key = "./certs/raspberry_pi_carson.private.key"                                # local path to Private key
device_id = "raspberry_pi_carson"
aws_url = "a1ryb83dujtssq-ats.iot.us-east-2.amazonaws.com"                                            # taken from AWS IoT Core

publish_topic = "iot/reading"  #the topic to be published to 
publish_qos = 1
subscribe_topic = "back/msgs" #the topic that will take commands
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


# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

lcd = True
#set up lcd object if it is not present then it does not crash the program
try:
    mylcd = I2C_LCD_Driver.lcd()
except:
    lcd = False

#set up the object for the rotary encoder
a = Button(16, pull_up=True)
b = Button(21, pull_up=True)
btn = Button(20, pull_up=True)

# read data using pin 14

#object for the ADC
mybus = smbus.SMBus(1)

#the menues array is for displaying the top menues of temp/humidity/potentiometer. the user must select from these
menues = [["Temperature","Push to select"],["Humidity","Push to select"],["Potentiometer","Push to select"]]
#the following variable is used for determining what the user selected from the menues page
#it starts at -1 because of the starting screen, if it were not then when the user moved the dial 
#it would skip the first menu to show the user
menues_page = -1 
sub_menu = 0 #a flag for determining if the program is in a sub menu or in a top menu
def pressed():
    global menues_page #sets the menues_page as a global variable 
    if b.value == 1: #determines if the rotarty encoder is turning clockwise
        if sub_menu == 0: #ill only change the 
            menues_page += 1
            if menues_page == (len(menues)):
                menues_page = 0
            mylcd.lcd_clear()
            mylcd.lcd_display_string(string=menues[menues_page][0])
            mylcd.lcd_display_string(string=menues[menues_page][1], line=2)

    elif b.value == 0: #determies if the rotarty encoder is turning counter-clockwise
        if sub_menu == 0:
            menues_page -= 1
            if menues_page == -1 or menues_page == -2:
                menues_page = len(menues)-1
            mylcd.lcd_clear()
            mylcd.lcd_display_string(string=menues[menues_page][0])
            mylcd.lcd_display_string(string=menues[menues_page][1], line=2)

def button():
    global sub_menu
    sub_menu += 1
    if sub_menu == 1 and menues_page == 0:
        po = "The Temp is:"
        po2 = "%-3.1f C" % result.temperature
        mylcd.lcd_clear()
        mylcd.lcd_display_string(string=po)
        mylcd.lcd_display_string(string=po2, line=2)
    elif sub_menu == 1 and menues_page == 1:
        po = "The Humidity is:"
        po2 = "%-3.1f %%" % result.humidity
        mylcd.lcd_clear()
        mylcd.lcd_display_string(string=po)
        mylcd.lcd_display_string(string=po2, line=2)
    elif sub_menu == 1 and menues_page == 2:
        po = "Potentiometer:"
        po2 = "%.2f " %percent
        mylcd.lcd_clear()
        mylcd.lcd_display_string(string=po)
        mylcd.lcd_display_string(string=po2, line=2)
    elif sub_menu == 2:
        sub_menu = 0
        mylcd.lcd_clear()
        mylcd.lcd_display_string(string=menues[menues_page][0])
        mylcd.lcd_display_string(string=menues[menues_page][1], line=2)
    
#callbacks for the rotary encoder
a.when_pressed = pressed 
btn.when_pressed = button

if lcd:#this if statement is to prevent the program from crashing 
    #starting screen for lcd
    mylcd.lcd_clear()
    greeting = ["Welcome, move","the dial 2 start"]
    mylcd.lcd_display_string(string=greeting[0])
    mylcd.lcd_display_string(string=greeting[1], line=2)

#main function and while loop
def main():
    while True:
        global result #global variable for the temp/humidity result
        global percent #global variable for the potentiometer result

        #sets up and reads temp/humidity from the DHT11
        temp_sensor = dht11.DHT11(pin = 25)
        result = temp_sensor.read()
        
        if result.is_valid():
            pass
        else:
            result = temp_sensor.read()
        
        #writes to the ADC the I2C address and the value calculated in lab
        mybus.write_byte(0x4b, 0x84)
        sleep(0.1)
        #reads from the ADC 
        to_print = mybus.read_byte(0x4b)
        #the following calculates and prints the percentage value of the rotation of the potentiometer
        percent = 100*(to_print/255)

        # creating dictionary {"voltage":"random integer"} and packing it into JSON format
        IoTmsg = dumps({'temperature':str("%-3.1f" % result.temperature),'humidity':str("%-3.1f" % result.humidity),'potentiometer':str("%.2f " %percent)})  
        awsClient.publish(publish_topic, IoTmsg, qos=publish_qos)    # publishing to topic
        #sleeps the main loop, this is done so data is not taken and sent constantly 
        sleep(5)

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

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        #this is for cleaning up the screen before exiting the program
        shut_down()
        mylcd.lcd_clear()
        goodbye = ["Thank you!","Have a Good Day!"]
        mylcd.lcd_display_string(string=goodbye[0],pos=int(((16/2)-(len(goodbye[0])/2))))
        mylcd.lcd_display_string(string=goodbye[1], line=2)
        sleep(3) #sleeps so that the message will be displayed before being cleared
        mylcd.lcd_clear()
        print("\nprogram exiting!")