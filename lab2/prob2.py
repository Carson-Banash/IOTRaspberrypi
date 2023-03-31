import smbus
from time import sleep

#object for the ADC
mybus = smbus.SMBus(1)

while True:
    #writes to the ADC the I2C address and the value calculated in lab
    mybus.write_byte(0x4b, 0x84)
    sleep(0.1)
    #reads from the ADC 
    to_print = mybus.read_byte(0x4b)
    #the following calculates and prints the percentage value of the rotation of the potentiometer
    percent = 100*(to_print/250)
    print("%.2f " %percent)




