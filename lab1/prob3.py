from gpiozero import Button, LED
#for the following functions, logical 0 supplies 0 volts and logical 1 supplies 3.3 volts
def b_pressed(): #function for when the button is pressed
	print("The button was pressed, turning on the red LED")
	red.value = 1 #sets the red led to on (logical 1)
	if blue.value == 1: #if the blue led is also on then this will run
		print("both the button and switch are on so turning on the green led")
		green.value = 1 #sets the green led on (logical 1)
def b_released(): #function for when the button is released
	print("The button was released, turning off the red LED")
	red.value = 0 #turns the red led off (logical 0)
	if blue.value == 1: #if the blue led is also on then this will run
		print("Button released so turning off the green led")
		green.value = 0 #sets the green led off (logical 0)

def s_on(): #function for when the slide switch is slid into the on position
	print("Switch slid to on position")
	blue.value = 1 #sets the blue led on (logical 1)
	if red.value == 1: #if the red led is also on then the following will execute
		print("Both the button and the switch are on so turning on green led")
		green.value = 1 #sets the green led on (logical 1)
def s_off(): #function for when the slide switch is slid into the off position
	print("Switch slid to off position")
	blue.value = 0 #sets the blue led off (logical 0)
	if red.value == 1: #if the red led is also on then the following will execute
		print("Slide is off and button is still on so turning off green led")
		green.value = 0 #sets the green led off (logical 0)

#sets up all of the different buttons, switches, and LED's
red = LED(22)
green = LED(19)
blue = LED(13)
button = Button(20, pull_up=True)
switch = Button(21, pull_up=True)

#defines which functions should be called when each button/slide is clicked/moved
switch.when_pressed = s_on
switch.when_released = s_off
button.when_pressed = b_pressed
button.when_released = b_released

#loop to continue running the program
while True:
	pass
