from gpiozero import Button

def pressed():
    if b.value == 1:
        print("The direction is clockwise")
    elif b.value == 0:
        print("The direction is counter-clockwise")
def button():
    print("the button was pressed")

a = Button(16, pull_up=True)
b = Button(21, pull_up=True)
btn = Button(20, pull_up=True)

a.when_pressed = pressed 
btn.when_pressed = button
while True:
	pass
