#!/usr/bin/python3

import Jetson.GPIO as GPIO
from time import sleep
import serial
from serial.tools import list_ports

def spray(box_to_print=None, 
            front_sprayer=0, 
            back_sprayer=0, 
            position=0, 
            sleeping=0,
            distance_corretion=0):
    '''
    After resizing the map to the quantity of sprayers per line the
    solenoid valves will open according to the position and kind of plant weed.
    Parameters:
        box_to_print: It's the variable containing the map with resized information to activate the sprayers
        front_sprayer: The list contaning the GPIO entrance for the first line in relation to the device, it will spray for class 50
        back_sprayer: The list contaning the GPIO entrance for the second line in relation to the device, it will spray for class 100
        position: Current position (when we create the map, we arealdy put the distance from the map to the
        first sprayer, the distance_corretion is used to consider the real distance from the first sprayer to 
        the second.)
        sleeping: Time interval between the activations
        distance_corretion: is used to consider the real distance from the first sprayer to the second in steps.

    Sprayers Design:
                    
                    (  ) - Camera
                     ||
                     ||
                     ||
                ------------
                |   Jetson  |
                |    Nano   |
                |           |
        ----------------------------
        |   0   0   0   0   0   0   |   Front sprayer
        |   0   0   0   0   0   0   |   Back Sprayer
        ----------------------------
    '''
    sprayers = len(front_sprayer) 
    
    try:
        print(f'[WEEDS] Spraying at position {position}')
        print('Values sprayed \n',box_to_print[-2-position:-position,:])
        print(' ', box_to_print[-position,:],'<----- Spraying Class 50 here')
        print(' ', box_to_print[-position+distance_corretion,:],'<----- Spraying Class 100 here')
        print(box_to_print[-position+1+distance_corretion:-position+3+distance_corretion,:])

        for pin in range(sprayers):
            
            # This is a workaround, I know there is an easier alternative, i`ll go through it later
            # Iterating through the first class == 50
            if box_to_print[-position,pin] == 50:
                GPIO.output(front_sprayer[pin], GPIO.HIGH)
            else:
                GPIO.output(front_sprayer[pin], GPIO.LOW)

            # Iterating through the second class == 100
            # I put a delay of X steps using the distance_corretion  
            if box_to_print[-position+distance_corretion,pin] == 100:
                GPIO.output(back_sprayer[pin], GPIO.HIGH)         
            else:
                GPIO.output(back_sprayer[pin], GPIO.LOW)
            sleep(sleeping)

    except KeyboardInterrupt:
        #Reset GPIO settings
        GPIO.output(front_sprayer, GPIO.LOW)
        GPIO.output(back_sprayer, GPIO.LOW)
        GPIO.cleanup()


def spray_arduino(box_to_print=None, 
            position=0, 
            sleeping=0,
            distance_corretion=0,
            serial_port=0):
    '''
    After resizing the map to the quantity of sprayers per line the
    solenoid valves will open according to the position and kind of plant weed.
    Parameters:
        box_to_print: It's the variable containing the map with resized information to activate the sprayers
        position: Current position (when we create the map, we arealdy put the distance from the map to the
        first sprayer, the distance_corretion is used to consider the real distance from the first sprayer to 
        the second.)
        sleeping: Time interval between the activations
        distance_corretion: is used to consider the real distance from the first sprayer to the second in steps.

    Sprayers Design:
                    
                    (  ) - Camera
                     ||
                     ||
                     ||
                ------------
                |   Jetson  |
                |    Nano   |
                |           |
        ----------------------------
        |   0   0   0   0   0   0   |   Front sprayer
        |   0   0   0   0   0   0   |   Back Sprayer
        ----------------------------
    '''
    sprayers = 6 # per line
    
    print(f'[WEEDS] Spraying at position {position}')
    print('Values sprayed \n',box_to_print[-2-position:-position,:])
    print(' ', box_to_print[-position,:],'<----- Spraying Class 50 here')
    print(' ', box_to_print[-position+distance_corretion,:],'<----- Spraying Class 100 here')
    print(box_to_print[-position+1+distance_corretion:-position+3+distance_corretion,:])

    '''
    i'll send to arduino a serial information, from the left to the right and from the front line to the back, 
    so i just need to send the state 0 or 1 and it will turn on or off there.
    '''
    pin_front = 2 # starts at 2 and goes to 7
    pin_back = 8 # starts at 8 and goes to 13
    for pin in range(sprayers):
        
        # This is a workaround, I know there is an easier alternative, i`ll go through it later
        # Iterating through the first class == 50
        if box_to_print[-position,pin] == 50 and position%10 == 0:
            info_front = f'ON{pin_front}\n'
            serial_port.write(info_front.encode('utf-8'))
            sleep(0.015)
            info_back = f'OFF{pin_back}\n'
            serial_port.write(info_back.encode('utf-8'))
            sleep(0.015)

            # As the pins will be always syncronized, i'll use the pin_front variable to update the pin_front and pin_back
            if pin_front == 7:
                pin_front = 2
                pin_back = 8
            else:
                pin_front += 1
                pin_back += 1

        # Iterating through the second class == 100
        # I put a delay of X steps using the distance_corretion  
        elif box_to_print[-position+distance_corretion,pin] == 100 and position%10 == 0:
            info_front = f'OFF{pin_front}\n'
            serial_port.write(info_front.encode('utf-8'))
            sleep(0.015)
            info_back = f'ON{pin_back}\n'
            serial_port.write(info_back.encode('utf-8'))
            sleep(0.015)

            # As the pins will be always syncronized, i'll use the pin_front variable to update the pin_front and pin_back
            if pin_front == 7:
                pin_front = 2
                pin_back = 8
            else:
                pin_front += 1
                pin_back += 1

        elif box_to_print[-position+distance_corretion,pin] == 0 and position%10 == 0:
            info_front = f'OFF{pin_front}\n'
            serial_port.write(info_front.encode('utf-8'))
            sleep(0.015)
            info_back = f'OFF{pin_back}\n'
            serial_port.write(info_back.encode('utf-8'))
            sleep(0.015)

            # As the pins will be always syncronized, i'll use the pin_front variable to update the pin_front and pin_back
            if pin_front == 7:
                pin_front = 2
                pin_back = 8
            else:
                pin_front += 1
                pin_back += 1

        sleep(sleeping)
