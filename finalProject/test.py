from gpiozero import LightSensor, MotionSensor
from time import sleep

pir = MotionSensor(25)
ldr = LightSensor(19, charge_time_limit=0.25)

while True:
    ldr_active = ldr.is_active
    if(ldr_active):
        print("ACTIVE")
    else:
        print("NOT")

    pir_active = pir.is_active
    if(pir_active):
        print("Motion Detected!")
    else:
        print("NOT")
    intensity = round(ldr.value * 100)
    print(intensity,"\n")
    sleep(2)