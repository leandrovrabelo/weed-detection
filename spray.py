#!/usr/bin/python3

import Jetson.GPIO as GPIO
from time import sleep

def spray(box_to_print=None, 
            sprayer_blue=0, 
            sprayer_red=0, 
            phis_dist=0, 
            position=0, 
            sleeping=0):

    sprayers = len(sprayer_blue) 
    
    try:
    
        print(f'[WEEDS] Spraying at position {position}')
        print('Values sprayed \n',box_to_print[-2-position:-position,:])
        print(' ', box_to_print[-position,:],'<----- Spraying Here')
        print(box_to_print[-position+1:-position+3,:])

        for pin in range(sprayers):
            
            if box_to_print[-position,pin] == 50:
                GPIO.output(sprayer_blue[pin], GPIO.HIGH)
                GPIO.output(sprayer_red[pin], GPIO.LOW)
              #  print('[WEEDS] Blue Printed',box_to_print[-position,pin],'pin',sprayer_blue[pin],'Position', position)

            elif box_to_print[-position,pin] == 100:
                GPIO.output(sprayer_red[pin], GPIO.HIGH)
                GPIO.output(sprayer_blue[pin], GPIO.LOW)
         #       print('[WEEDS] Red Printed',box_to_print[-position,pin],'pin',sprayer_red[pin],'Position', position)

            else:
                GPIO.output(sprayer_blue[pin], GPIO.LOW)
                GPIO.output(sprayer_red[pin], GPIO.LOW)
       #         print('[WEEDS] Nothing printed')
            sleep(sleeping)

    except KeyboardInterrupt:
        #Reset GPIO settings
        GPIO.output(sprayer_blue, GPIO.LOW)
        GPIO.output(sprayer_red, GPIO.LOW)
        GPIO.cleanup()

if __name__ == '__main__':

    spray()