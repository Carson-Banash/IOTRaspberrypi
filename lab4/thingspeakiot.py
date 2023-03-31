import RPi.GPIO as GPIO
import dht11_library as dht11
import smbus
from gpiozero import Button
import I2C_LCD_Driver
from time import sleep
import paho.mqtt.client as mqtt


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

MQTT_CLIENT_ID = "OzwMAQQzAj0kMysALiEpFyg" # This is for your own client identification. Can be anything
MQTT_USERNAME = "OzwMAQQzAj0kMysALiEpFyg" #This is the ThingsSpeak's Author
MQTT_PASSWD = "qDfhDyahMxKMtdWrDwLAkVaP" #This is the MQTT API Key found under My Profile in ThingSpeak
MQTT_HOST = "mqtt3.thingspeak.com" #This is the ThingSpeak hostname
MQTT_PORT = 1883 #Typical port # for MQTT protocol. If using TLS -> 8883
CHANNEL_ID = "1916731" #Channel ID found on ThingSpeak website
MQTT_WRITE_APIKEY = "Y20O9QUIESJ7OPEA" # Write API Key found under ThingSpeak Channel Settings
MQTT_PUBLISH_TOPIC = "channels/" + CHANNEL_ID + "/publish"
""" 
Standard callback functions. See Phao MQTT documentation for more

This function will be called upon connection
"""

def on_connect(client, userdata, flags, rc):
    print("Connected ", rc)

"""
This function is called upon Publishing of data to predefined topic
"""

def on_publish(client, userdata, result):
    print("Published ", result)

""" 
This function is used for logging. For this to work, you must uncomment the callback binding
"""

def on_log(client, userdata, level, buf):
    print("log:", buf)


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
        if sub_menu == 0: #ill only chage the 
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
    global client
    """ create client instance"""
    client = mqtt.Client(client_id=MQTT_CLIENT_ID, clean_session=True, userdata=None, protocol=mqtt.MQTTv311, transport="tcp")
    
    """ standard callback bindings """
    #client.on_connect = on_connect
    #client.on_message = on_message
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

    while True:
        global result #global variable for the temp/humidity result
        global percent #global variable for the potentiometer result

        if not client.is_connected:
            print("Client disconnected. Trying to reconnect.")
            client.reconnect()

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

        pub_topic = "field1=" + str("%-3.1f" % result.temperature) + "&field2=" + str("%-3.1f" % result.humidity) + "&field3=" + str("%.2f " %percent) 
        #print(MQTT_PUBLISH_TOPIC,"\n",pub_topic,"\n")
        client.publish(MQTT_PUBLISH_TOPIC, pub_topic)

        #sleeps the main loop, this is done so data is not taken constantly 
        sleep(5)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        #this is for cleaning up the screen before exiting the program
        mylcd.lcd_clear()
        goodbye = ["Thank you!","Have a Good Day!"]
        mylcd.lcd_display_string(string=goodbye[0],pos=int(((16/2)-(len(goodbye[0])/2))))
        mylcd.lcd_display_string(string=goodbye[1], line=2)
        sleep(3) #sleeps so that the message will be displayed before being cleared
        mylcd.lcd_clear()
        client.disconnect()
        print("\nprogram exiting!")