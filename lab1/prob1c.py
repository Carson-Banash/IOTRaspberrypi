from gpiozero import LED
from time import sleep
#sets the LED up using gpio 19
led = LED(19)

#runns forever
while True:
	led.value=1 #sets the value of the led to 1 (3.3v is supplied)
	sleep(0.5) #pauses for 0.5 seconds
	led.value=0 #sets the value of the led to 0 (0v is supplied)
	sleep(0.5) #pauses for 0.5 seconds
