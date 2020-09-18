#!/usr/bin/python3

from datetime import datetime
import Jetson.GPIO as GPIO
import sys
import numpy as np
GPIO.setmode(GPIO.BOARD)

curr_position = 0
counter_speed = 0
counter_infer_photo = 0
counter_check_photo = 0   
start = datetime.now()
speed = 0

def mov_detector(gpio_sensor=0, 
                cm_hole=0,
                disk_hole_qtt=0, 
                height=0, 
                infer_trigger=False, 
                check_trigger=False, 
                start_photo_inference=0, 
                start_photo_check=0, 
                spray_line1=0, 
                spray_line2=0):
                
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

        if GPIO.wait_for_edge(gpio_sensor, GPIO.FALLING): # Change in signal
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
                if counter_infer_photo * cm_hole >= height:
                    infer_trigger = True
                    counter_infer_photo = 0
                    print('[WEEDS] Inference Photo Triggered')
                else:
                    infer_trigger = False

            # Triggering Check Photo
            if curr_position >= start_photo_check:
                if counter_check_photo * cm_hole >= height:
                    check_trigger = True
                    counter_check_photo = 0
                    print('[WEEDS] Check Photo Triggered')
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