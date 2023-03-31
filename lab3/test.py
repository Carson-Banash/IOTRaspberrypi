import I2C_LCD_Driver
from time import *

mylcd = I2C_LCD_Driver.lcd()

while True:
    mylcd.lcd_display_string("Hello world!123456789",2)
    time.sleep(1)
    mylcd.lcd_clear()
    time.sleep(1)