from gpiozero import LED
from time import sleep

led = LED(13) #sets the led with gpio pin 19

while True:
	ans = input("On or Off? ") #asks the user to input the state of the led
	ans = ans.lower()
	if ans == 'on': #if the user anwsered on then the value of the gpio pin is set to 1 (3.3v is supplied)
		led.value = 1
	if ans == 'off': #if the user anwsered off then the value of the gpio pin is set to 0 (0v is supplied)
		led.value = 0

