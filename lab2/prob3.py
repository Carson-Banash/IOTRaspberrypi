from gpiozero import PWMOutputDevice
from time import sleep
#led object using pwm
led = PWMOutputDevice(13) 

while True:
    #this for loop is for making the led brighter (0->100)
    for num in range(0,100):
        power = num/100 #gets a value from 0 to 1
        led.value = power #sets the led value to the coresponding value
        sleep(0.025) 
    for num2 in range(100,0,-1):
        power = num2/100 #gets a value from 1 to 0
        led.value = power #sets the led value to the coresponding value
        sleep(0.025)



