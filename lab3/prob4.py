import I2C_LCD_Driver

mylcd = I2C_LCD_Driver.lcd()

while True:
    print("welcome to the lcd python script!! \nPlease select one of the following options")
    print("\t1 - print name centered\n\t2 - print custom characters\n\t3 - clear the screen")
    choice = int(input("Please make your selection: "))

    if choice == 1:
        mylcd.lcd_clear()
        firstn = "Carson"
        lastn = "Banash"
        mylcd.lcd_display_string(string=firstn,pos=int(((16/2)-(len(firstn)/2))))
        mylcd.lcd_display_string(string=lastn,line=2,pos=int(((16/2)-(len(lastn)/2))))

    elif choice == 2:
        mylcd.lcd_clear()
        chars = [
            [0b00000,
            0b11011,
            0b11011,
            0b11011,
            0b00000,
            0b10001,
            0b01110,
            0b00000],

            [0b10101,
            0b01010,
            0b10101,
            0b01010,
            0b10101,
            0b01010,
            0b10101,
            0b01010]
        ]
        mylcd.lcd_load_custom_chars(chars)
        mylcd.lcd_write(0x80)
        mylcd.lcd_write_char(0)
        mylcd.lcd_display_string(chr(1),line=2,pos=5)

    elif choice == 3:
        mylcd.lcd_clear()   
    else:
        print("Please choose one of the three options!")
