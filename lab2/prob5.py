import smbus
from gpiozero import PWMOutputDevice
from gpiozero import Button
from time import sleep

#creating the led objects
rled = PWMOutputDevice(13)
bled = PWMOutputDevice(19)
gled = PWMOutputDevice(26)
#creating the ADC and button objects
mybus = smbus.SMBus(1)
button = Button(20,pull_up=True)

#array of each of the led objects, this is for switching between them as the button is clicked
leds = [rled,bled,gled]
#sets the initial value of position
position = 0

#function for when the button is pressed
def pressed():
    #the following loops the array back to zero when the user reaches the end
    global position
    if position == 2:
        position = 0
    else:
        position = position + 1

button.when_pressed = pressed

while True:

    mybus.write_byte(0x4b, 0x84)
    sleep(0.1)
    to_print = mybus.read_byte(0x4b) #reads the value of the potentiometer

    #gets a value of zero to one of the location of the potentiometer
    power = (to_print/255)
    #sets the selected leds value (brightness) to the potentiometer value
    leds[position].value = (power)