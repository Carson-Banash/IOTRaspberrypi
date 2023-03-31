from gpiozero import Button

def pressed(): #defines the callback function pressed
	print("The Button was Pressed")
def released(): #defines the callback function released
	print("The Button was Released")

#setst the button up using gpio pin 20, with the pull up on
button = Button(20, pull_up=True)

button.when_pressed = pressed #when the button is pressed the function pressed is called
button.when_released = released #when the button is released the function released is called
#the following is just a loop to continue running the program
while True:
	pass
