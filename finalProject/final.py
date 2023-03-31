from gpiozero import LightSensor, MotionSensor, Button
from time import sleep
import I2C_LCD_Driver
           
from paho.mqtt import client as mqtt
import ssl, re, os 
from json import dumps, loads   

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

pir = MotionSensor(25)
ldr = LightSensor(19, charge_time_limit=0.09)

#set up the object for the rotary encoder
a = Button(16, pull_up=True)
b = Button(21, pull_up=True)
btn = Button(20, pull_up=True)

try:
    lcd = I2C_LCD_Driver.lcd()
except:
    lcd = False

menues = [["Toggle Light","Push to toggle"],["Motions Sensor","Push to select"],["Light Sensor","Push to select"]]

menues_page = -1 
sub_menu = 0 #a flag for determining if the program is in a sub menu or in a top menu
def pressed():
    global menues_page #sets the menues_page as a global variable 
    if b.value == 1: #determines if the rotarty encoder is turning clockwise
        if sub_menu == 0: #will only chage the screen if in the main menu
            menues_page += 1
            if menues_page == (len(menues)):
                menues_page = 0
            lcd.lcd_clear()
            lcd.lcd_display_string(string=menues[menues_page][0])
            lcd.lcd_display_string(string=menues[menues_page][1], line=2)

    elif b.value == 0: #determies if the rotarty encoder is turning counter-clockwise
        if sub_menu == 0:
            menues_page -= 1
            if menues_page == -1 or menues_page == -2:
                menues_page = len(menues)-1
            lcd.lcd_clear()
            lcd.lcd_display_string(string=menues[menues_page][0])
            lcd.lcd_display_string(string=menues[menues_page][1], line=2)

def button():
    global flag
    global sub_menu
    sub_menu += 1
    if sub_menu == 1 and menues_page == 0:
        if flag == 0:
            flag = 1
        elif flag == 1:
            flag = 0
        IoTmsg = dumps({'switch':flag})
        awsClient.publish(publish_topic, IoTmsg, qos=publish_qos)
        
        po = "The light has toggled"
        po2 = "been toggled"
        lcd.lcd_clear()
        lcd.lcd_display_string(string=po)
        lcd.lcd_display_string(string=po2, line=2)
    elif sub_menu == 1 and menues_page == 1:
        po = "Motion read out:"
        if(pir_active):
            po2 = "There is motion"
        else:
            po2 = "No motion found"
        lcd.lcd_clear()
        lcd.lcd_display_string(string=po)
        lcd.lcd_display_string(string=po2, line=2)
    elif sub_menu == 1 and menues_page == 2:
        if(pir_active):
            status = "detected"
        else:
            status = "not found"
        po = "Light: %s" %status
        po2 = "Intensity= %.2d%%" %(intensity)
        lcd.lcd_clear()
        lcd.lcd_display_string(string=po)
        lcd.lcd_display_string(string=po2, line=2)
    elif sub_menu == 2:
        sub_menu = 0
        lcd.lcd_clear()
        lcd.lcd_display_string(string=menues[menues_page][0])
        lcd.lcd_display_string(string=menues[menues_page][1], line=2)

#callbacks for the rotary encoder
a.when_pressed = pressed 
btn.when_pressed = button

if lcd:#this if statement is to prevent the program from crashing 
    #starting screen for lcd
    lcd.lcd_clear()
    greeting = ["Welcome, move","the dial 2 start"]
    lcd.lcd_display_string(string=greeting[0])
    lcd.lcd_display_string(string=greeting[1], line=2)

def main():
    past_flag = 0
    
    while True:
        global ldr_active
        global intensity
        global pir_active
        global flag
        
        intensity = ldr.value * 100
        pir_active = pir.is_active

        if(intensity > 60):
            light = True
        else:
            light = False

        if(light):
            pass
            #turn light off
            flag = 0
            print("OFF: LIGHT")
            print(intensity)
        elif(not light and pir_active):
            pass
            #turn light on
            flag = 1
            print("ON: dark, motion")
        elif(not light and not pir_active):
            pass
            #turn light off
            flag = 0
            print("OFF: dark, no motion")
        
        if past_flag != flag:
            IoTmsg = dumps({'switch':flag})   
            print("flag is %d" %flag)
            awsClient.publish(publish_topic, IoTmsg, qos=publish_qos)

        past_flag = flag 

        sleep(5)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        #this is for cleaning up the screen before exiting the program
        lcd.lcd_clear()
        shut_down()
        lcd.lcd_clear()
        goodbye = ["Thank you!","Have a Good Day!"]
        lcd.lcd_display_string(string=goodbye[0],pos=int(((16/2)-(len(goodbye[0])/2))))
        lcd.lcd_display_string(string=goodbye[1], line=2)
        sleep(3) #sleeps so that the message will be displayed before being cleared
        lcd.lcd_clear()
        print("\nprogram exiting!")