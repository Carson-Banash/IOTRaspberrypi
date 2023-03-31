from gpiozero import LED

#sets the LED up using gpio 19
led = LED(19)

#uses the blink method with 0.5 seconds on and off and blinks for 10 times
led.blink(on_time=0.5,off_time=0.5,n=10)
