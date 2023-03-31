import smbus
from time import sleep

mybus = smbus.SMBus(1)

while True:
    mybus.write_byte(0x4b, 0x84)
    sleep(0.1)
    to_print = mybus.read_byte(0x4b)
    space = int(to_print/10)
    other_side = int(25-space)
    print('|'+' '*space+"==="+' '*other_side+'|')




