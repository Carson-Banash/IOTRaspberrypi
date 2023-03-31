from gpiozero import LED
from time import sleep

#all of the different segments for the seven leds 
a = LED(18)
b = LED(25)
c = LED(19)
d = LED(6)
e = LED(5)
f = LED(24)
g = LED(23)

#array of the led objects used to loop though them and set each value
objects = [a,b,c,d,e,f,g]

#2d array of all of the values of each led 1=on 0=off. 
#the first array coresponds to zero and the last is nine
all_nums = [[1,1,1,1,1,1,0], [0,1,1,0,0,0,0], [1,1,0,1,1,0,1],
    [1,1,1,1,0,0,1], [0,1,1,0,0,1,1], [1,0,1,1,0,1,1], [1,0,1,1,1,1,1],
    [1,1,1,0,0,0,0], [1,1,1,1,1,1,1], [1,1,1,1,0,1,1]]

while True:
    #prompts the user for a choice of rotate (rotates 0-9) choose (choose 0-9 to display) and off
    ans = input("rotate, choose, off? ")
    ans = ans.lower() #lowercases the user input for use in the program

    if ans == 'rotate':
        #
        for nums in range(11):
            i = 0
            if nums == 10:
                for leds in objects:
                    leds.value = 0
                break
            for leds in objects:
                leds.value = all_nums[nums][i]
                i += 1
            sleep(1)

    elif ans == 'choose':
        num = int(input("enter a number to display: "))
        i=0
        for leds in objects:
            leds.value = all_nums[num][i]
            i += 1

    elif ans == 'off':
        for leds in objects:
            leds.value = 0