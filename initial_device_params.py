#!/usr/bin/python

import Jetson.GPIO as GPIO
from time import sleep
import sys
GPIO.setmode(GPIO.BOARD)

def turn_on_pumps(left_pump=0,
                right_punp=0):
    try:
        # Setting initial values for sprayers
        GPIO.setup(left_pump, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(right_punp, GPIO.OUT, initial=GPIO.HIGH)

    except KeyboardInterrupt:
        print("[WEEDS] Turning off the pumps.")
        GPIO.output(left_pump, GPIO.LOW)
        GPIO.output(right_punp, GPIO.LOW)
        GPIO.cleanup()
        sys.exit()


def remove_air_sprays(front_sprayer=None, 
                    back_sprayer=None,
                    time_interval=8):

    try:
        # Quantity of sprayers
        sprayers = len(front_sprayer)

        # Setting initial values for sprayers
        GPIO.setup(front_sprayer, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(back_sprayer, GPIO.OUT, initial=GPIO.LOW)

        # Initiating spray from the last one until the closest to the bar
        
        print(f'[WEEDS] OPENING the pin {front_sprayer[-1]} of the blue sprayer')
        print(f'[WEEDS] OPENING the pin {back_sprayer[-1]} of the red sprayer\n')
        GPIO.output(front_sprayer[-1], GPIO.HIGH)
        GPIO.output(back_sprayer[-1], GPIO.HIGH)
        sleep(time_interval)
        
        for index in range(1, sprayers):
            
            print(f'[WEEDS] CLOSING the pin {front_sprayer[-index]} of the blue sprayer')
            print(f'[WEEDS] CLOSING the pin {back_sprayer[-index]} of the red sprayer\n')
            GPIO.output(front_sprayer[-index], GPIO.LOW)
            GPIO.output(back_sprayer[-index], GPIO.LOW)
            sleep(time_interval)

            print(f'[WEEDS] OPENING the pin {front_sprayer[-index - 1]} of the blue sprayer')
            print(f'[WEEDS] OPENING the pin {back_sprayer[-index - 1]} of the red \n')

            GPIO.output(front_sprayer[-index - 1], GPIO.HIGH)
            GPIO.output(back_sprayer[-index - 1], GPIO.HIGH)
            sleep(time_interval)

        print(f'[WEEDS] CLOSING the pin {front_sprayer[-sprayers]} of the blue sprayer')
        print(f'[WEEDS] CLOSING the pin {back_sprayer[-sprayers]} of the red sprayer\n')
        GPIO.output(front_sprayer[-sprayers], GPIO.LOW)
        GPIO.output(back_sprayer[-sprayers], GPIO.LOW)
    
    except KeyboardInterrupt:
        print("[WEEDS] Turning off the sprayers.")
        GPIO.output(front_sprayer, GPIO.LOW)
        GPIO.output(back_sprayer, GPIO.LOW)
        GPIO.cleanup()
        sys.exit()
