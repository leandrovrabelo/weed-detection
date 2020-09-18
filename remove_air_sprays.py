#!/usr/bin/python

import Jetson.GPIO as GPIO
from time import sleep
import sys
GPIO.setmode(GPIO.BOARD)

def remove_air_sprays(sprayer_blue=None, 
                    sprayer_red=None):

    try:
        # Quantity of sprayers
        sprayers = len(sprayer_blue)

        # Setting initial values for sprayers
        GPIO.setup(sprayer_blue, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(sprayer_red, GPIO.OUT, initial=GPIO.LOW)

        # Initiating spray from the last one until the closest to the bar
        
        print(f'[WEEDS] OPENING the pin {sprayer_blue[-1]} of the blue sprayer')
        print(f'[WEEDS] OPENING the pin {sprayer_red[-1]} of the red sprayer\n')
        GPIO.output(sprayer_blue[-1], GPIO.HIGH)
        GPIO.output(sprayer_red[-1], GPIO.HIGH)
        sleep(8)
        
        for index in range(1, sprayers):
            
            print(f'[WEEDS] CLOSING the pin {sprayer_blue[-index]} of the blue sprayer')
            print(f'[WEEDS] CLOSING the pin {sprayer_red[-index]} of the red sprayer\n')
            GPIO.output(sprayer_blue[-index], GPIO.LOW)
            GPIO.output(sprayer_red[-index], GPIO.LOW)
            sleep(1)

            print(f'[WEEDS] OPENING the pin {sprayer_blue[-index - 1]} of the blue sprayer')
            print(f'[WEEDS] OPENING the pin {sprayer_red[-index - 1]} of the red \n')

            GPIO.output(sprayer_blue[-index - 1], GPIO.HIGH)
            GPIO.output(sprayer_red[-index - 1], GPIO.HIGH)
            sleep(2)

        print(f'[WEEDS] CLOSING the pin {sprayer_blue[-sprayers]} of the blue sprayer')
        print(f'[WEEDS] CLOSING the pin {sprayer_red[-sprayers]} of the red sprayer\n')
        GPIO.output(sprayer_blue[-sprayers], GPIO.LOW)
        GPIO.output(sprayer_red[-sprayers], GPIO.LOW)
    
    except KeyboardInterrupt:
        print("[WEEDS] KeyboardInterrupt has been caught.")
        GPIO.output(sprayer_blue, GPIO.LOW)
        GPIO.output(sprayer_red, GPIO.LOW)
        GPIO.cleanup()
        sys.exit()
    
if __name__ == '__main__':
    remove_air_sprays()