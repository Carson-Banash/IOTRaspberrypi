from gpiozero import Button
from time import time
#sets the button up using gpio 20 and the pull up on
button = Button(20,pull_up=True)

def pressed(): #function for the button press
	print("Pressed")
	global p_time #sets up a global variable (for use by the released function)
	p_time = time() #gets the time that the button was pressed

def released(): #function for the button release
	print("Released")
	r_time = time() #gets the time that the button was released
	#sets the held time variable as the difference between the time released and the time held
	t_held = r_time - p_time
	#prints the time held to the screen with 2 decimal places
	print("The button was held for %.2f seconds"  %t_held)

button.when_pressed = pressed #when the button is pressed, calls the pressed funciton
button.when_released = released #when the button is released, calls the released function

#loop to continue running the program
while True:
	pass
