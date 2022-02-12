#!/usr/bin/python3

from datetime import datetime
import Jetson.GPIO as GPIO
import sys
import numpy as np
GPIO.setmode(GPIO.BOARD)

curr_position = 0 # Starting position
counter_speed = 0 
counter_infer_photo = 0
counter_check_photo = 0   
start = datetime.now()
speed = 0

def mov_detector(gpio_sensor=0, 
                cm_hole=0,
                distance_interval=0, 
                start_photo_inference=0, 
                start_photo_check=0, 
                spray_line1=0, 
                spray_line2=0):

    '''
    In this function we will use a disk with 20 or 40 holes and a radius of 5.1 cm,
    the the end of the disk (perpendicular), we will use an infrared sensor to detect interruptions,
    every interruption is a movement.

    It will also be used to check the speed, trigger a photo for inference and checage.
    Parameters:
            gpio_sensor: this is the device port to connect as an input
            cm_hole: it means how many centimeters each hole in the disk has (it's one step in the disk)
            distance_interval: This is the distance in CM to be defined to trigger a photo
            start_photo_inference: the minimal distance to trigger the photo for inference
            start_photo_check: the minimal distance to trigger the check photo (check the spray)
            spray_line1: if KeyBoard interrupt is triggered it turns off the solenoids in the first line
            spray_line2: if KeyBoard interrupt is triggered it turns off the solenoids in the second line
    
    # TODO:
            Use two sensors to detect the direction of the disk
    '''
    GPIO.setup(gpio_sensor, GPIO.IN)
    # Setting initial time to measure the speed
    global curr_position
    global counter_speed
    global counter_infer_photo
    global counter_check_photo
    global start
    global speed

    try:
        if counter_speed == 0:
            start = datetime.now()

        if GPIO.wait_for_edge(gpio_sensor, GPIO.RISING):
            pass

        if GPIO.wait_for_edge(gpio_sensor, GPIO.FALLING): # Change in signal, counting steps
            curr_position += 1
            counter_speed += 1
            counter_infer_photo += 1
            counter_check_photo += 1

            # Measuring distance travelled
            distance = curr_position * cm_hole # LOOK AT THIS 
            print('[WEEDS] Distance Traveled: ', round(distance / 100, 4),' meters')

            # Measuring variation on time and distance
            if counter_speed == 10:
                end = datetime.now()
                diff = end - start
                delta_time = diff.seconds + diff.microseconds/1e6
                delta_distance = counter_speed * cm_hole / 100 #in meters
                speed = delta_distance / delta_time # m/sec
                counter_speed = 0

            if curr_position > 10:
                print('[WEEDS] Current speed: ', round(speed,2),' m/sec or: ', round(speed * 3.6, 2),' km/h.')
            # Triggering Inference Photo
            if curr_position >= start_photo_inference:
                if counter_infer_photo * cm_hole >= distance_interval:
                    infer_trigger = True
                    counter_infer_photo = 0
                    print('[WEEDS] Inference Photo Triggered')
                else:
                    infer_trigger = False
            else:
                infer_trigger = False

            # Triggering Check Photo
            if curr_position >= start_photo_check:
                if counter_check_photo * cm_hole >= distance_interval:
                    check_trigger = True
                    counter_check_photo = 0
                    print('[WEEDS] Check Photo Triggered')
                else:
                    check_trigger = False
            else:
                check_trigger = False


        print('[WEEDS] Position:', curr_position,', Infer Trigger:', infer_trigger,', Check Trigger:', check_trigger)

    except KeyboardInterrupt:
        print("[WEEDS] KeyboardInterrupt has been caught.")
        GPIO.output(spray_line1, GPIO.LOW)
        GPIO.output(spray_line2, GPIO.LOW)
        GPIO.cleanup()
        sys.exit()

    return curr_position, infer_trigger, check_trigger
