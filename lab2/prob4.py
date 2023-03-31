import smbus
from gpiozero import PWMOutputDevice
from time import sleep

#sets up the led and ADC
led = PWMOutputDevice(13) 
mybus = smbus.SMBus(1)

while True:
    #sets up the ADC 
    mybus.write_byte(0x4b, 0x84)
    sleep(0.1)
    #reads the value from the potentiometer
    to_print = mybus.read_byte(0x4b)
    #calculates the power level from the potentiometer (0-1) 
    power = (to_print/254)
    #sets the led value to the calculated power value from the potentiometer (0-1)
    led.value = power 