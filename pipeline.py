#!/usr/bin/python3
import csv
import sys
import cv2
import os
import sys
import numpy as np
from time import sleep
import Jetson.GPIO as GPIO
from datetime import datetime
import coco_weeds
import jetson.inference
import jetson.utils
from create_csv import create_csv
from mov_detector import mov_detector
from camera_pipeline import camera_pipeline
from photo_inference import camera_inference
from resize_adjust_bbox_map import resize_adjust_bbox_map
from calibration import calibrate, find_values_to_adjust, find_values_to_adjust_by_index
from spray import spray
from check_spray import check_spray
from remove_air_sprays import remove_air_sprays
from set_dimentions import set_dimentions
GPIO.setwarnings(False)

if __name__ == '__main__':

    # Loading the Inference Model and other informations
    COCO_LABELS = coco_weeds.COCO_CLASSES_LIST
    threshold = 0.5
    print('[WEEDS] Loading the Inference Classes: ')
    print(f'[WEEDS] Classes: {COCO_LABELS[1:]}')
    print(f'[WEEDS] Inference Threshold Value: {threshold}') 
    print('[WEEDS] Loading DETECNET WEEDS MODEL')
    detection_model = jetson.inference.detectNet(threshold=threshold)
    print('[WEEDS] DETECNET WEEDS MODEL Loaded')
    reshape_value = 300
    print(f'[WEEDS] The inference photo will be reshaped with the value of {reshape_value}')

    # Sensor configuration
    gpio_sensor = 7
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(gpio_sensor, GPIO.IN)
    print('[WEEDS] Setting as Input the GPIO in the Rotary sensor with the number:', gpio_sensor)

    # Information related to the dimentions the rotary disk
    disk_radius = 5.10
    disk_hole_qtt = 40
    height = 80 # This is the desired height of the photo in cm
    width = 120 # This is the desired width of the photo in cm
    cm_hole = (2 * disk_radius * np.pi) / disk_hole_qtt
    walked_positions = int(round(height / cm_hole,0))
    print('[WEEDS] Rotary encoder information:')
    print('[WEEDS] Radius:                     ', disk_radius, '(cm)')
    print('[WEEDS] Hole qtt in disk:           ', disk_hole_qtt,'cm')
    print('[WEEDS] Centimeter per hole:        ', round(cm_hole,4), 'cm')
    print('[WEEDS] Desired HEIGTH of the photo (cm that the camera will capture in the ground):', height,'cm')
    print('[WEEDS] Desired WIDTH of the photo (cm that the camera will capture in the ground):', width,'cm')

    # Information related to the measurement of velocity, position and triggers
    curr_position = 0 # infinite rotation counter
    counter_speed = 0 # If this value reach a complete circle on the disk it will measure the speed
    infer_trigger = False # If True it will take a photo to make an inference
    counter_infer_photo = 0 # This will be the counter to trigger the inference photo
    check_trigger = False # if True ir will take a photo to check the sprays 
    counter_check_photo = 0 # This will be the counter to trigger the check spray photo
    check_photos_qtt = 0

    # Information related to the dimensions of the equipment and values to take the photo
    cameras_box_distance = 6 # this is the distance between the center of the box and the begining of the arm in cm
    arm_holders_distance = 5 # this is the distance from the box to the hole of the end/begining of the arm
    inference_stick = 50 # size of the arms used to hold the USB camera in cm
    checking_stick = 90 # size of the arms used to hold the CSI camera in cm
    equip_depth = 105 # This is the height from the ground until the beginning of the arms.
    equip_lenght = 70 # in cm
    first_sprayer_dist = 2 # distance from the main equipment to the beginning of the first sprayer

    (value_to_cut_usb_width_photo, 
    value_to_cut_csi_width_photo, 
    new_usb_arm_size, 
    new_csi_arm_size) = set_dimentions(
                                        desired_height=height, 
                                        desired_width=width, 
                                        infer_stick=inference_stick,
                                        check_stick=checking_stick,
                                        equip_depth=equip_depth)

    # These values will be converted from centimeters to steps (cm_holes)
    start_infer_photo = int(20 / cm_hole) # Initial distance to start taking infer photos

    dist_infer_spray = int((cameras_box_distance + 
                            arm_holders_distance * 2 +
                            new_usb_arm_size + 
                            equip_lenght + 
                            first_sprayer_dist) / 
                            cm_hole) # Distance between the camera and the first sprayers

    dist_between_cameras = int((cameras_box_distance * 2 + 
                                arm_holders_distance * 4 +
                                new_usb_arm_size + 
                                equip_lenght + 
                                new_csi_arm_size) / 
                                cm_hole) # Distance between infer camera and check camera

    if start_infer_photo < int(height/cm_hole):
        start_check_photo = dist_between_cameras # Initial distance to start taking checking photos
    else: 
        start_check_photo = dist_between_cameras + start_infer_photo # Initial distance to start taking checking photos
    print(f'[WEEDS] The equipment lenght is {equip_lenght} cm')
    print('[WEEDS] Setting the distance between the INFER CAMERA and the SPRAYS as', dist_infer_spray, 'steps')
    print('[WEEDS] Setting the distance between the CAMERAS as', dist_between_cameras, 'steps')    
    print(f'[WEEDS] The Check photos will start after {start_check_photo} steps')
    print(f'[WEEDS] Each Inference and Checking photo will be taken after {walked_positions} steps ({height} cm).\n')

    # Paths
    print('[WEEDS] Loading paths for CSV files, Infer, BBox and Check photos')
    path_to_csv = '/PATHTOSAVEFILES/weed_detection/saved_files/csv/'
    path_to_photos = '/PATHTOSAVEFILES/weed_detection/saved_files/fotos/'
    path_to_bbox_photos = '/PATHTOSAVEFILES/weed_detection/saved_files/bbox_photo/'
    path_to_check_photos = '/PATHTOSAVEFILES/weed_detection/saved_files/check_photo/'

    # Creating a CSV file
    print('[WEEDS] Creating a CSV FILE')
    csv_file = create_csv(path_to_csv)
    print(f'[WEEDS] CSV file created on {csv_file}')

    # Acessing the cameras for inference and check the sprays
    pixels_width = 640 # Pixels
    pixels_height = 480 # Pixels
    print(f'[WEEDS] Setting Informations: WIDTH - {pixels_width} pixels, HEIGHT - {pixels_height} pixels')

    infer_cam_type = 'usb'
    infer_camera = camera_pipeline(capture_width=pixels_width, 
                                    capture_height=pixels_height, 
                                    framerate=120, 
                                    flip_method=0, 
                                    cam_type=infer_cam_type)
    check_cam_type = 'csi'
    check_camera = camera_pipeline(capture_width=1280, 
                                    capture_height=720, 
                                    display_width=pixels_width, 
                                    display_height=pixels_height, 
                                    framerate=120, 
                                    flip_method=0, 
                                    cam_type=check_cam_type)

    print(f'[WEEDS] Inference Camera selected - [{infer_cam_type}]')
    print(f'[WEEDS] Check Camera selected     - [{check_cam_type}]')
    
    sprayers = 12 # quantity
    sprayer_lines = 2
    sprayers_per_line = int(sprayers/sprayer_lines)
    print(f'[WEEDS] Sprayer information:')
    print(f'[WEEDS] Sprayer quantity:  {sprayers} sprayers')
    print(f'[WEEDS] Individual lines:  {sprayer_lines}')
    print(f'[WEEDS] Sprayers per line: {sprayers_per_line}')

    box_to_print = np.zeros((dist_infer_spray, sprayers_per_line), np.uint8)
    dif_calib_start = np.zeros(sprayers_per_line, np.uint8) # two lines of sprayers
    dif_calib_end = np.zeros(sprayers_per_line, np.uint8) # two lines of sprayers

    # Variables that are going to be used in the spray function
    GPIO.setmode(GPIO.BOARD)
    sleep_time = 0.001
    blue_pins = [11, 12, 13, 15, 16, 18] # Pins for blue ink
    blue_dict = {x:y for x,y in enumerate(blue_pins)}
    GPIO.setup(blue_pins, GPIO.OUT, initial=GPIO.LOW)
    print(f'[WEEDS] Loading the FIRST line sprayer as OUTPUT with the following GPIO pins: {blue_pins}')

    red_pins = [19, 21, 22, 23, 38, 40] # Pins for red ink
    red_dict = {x:y for x,y in enumerate(red_pins)}
    GPIO.setup(red_pins, GPIO.OUT, initial=GPIO.LOW)
    print(f'[WEEDS] Loading the SECOND line sprayer as OUTPUT with the following GPIO pins: {red_pins}')
    
    # print('[WEEDS] Preparing to remove air from the sprayers')
    # remove_air_sprays(sprayer_blue=blue_pins, 
    #                     sprayer_red=red_pins)
    # print('[WEEDS] Air removal proccess completed')

    print('[WEEDS] THE SYSTEM IS READY TO WORK')

    while True:
           
        ret1, infer_photo = infer_camera.read()
        # cv2.imshow('INFER CAMERA', infer_photo)

        if ret1 == False:
            break

        ret2, check_photo = check_camera.read()
        # cv2.imshow('CHECK CAMERA', check_photo)
        if ret2 == False:

            sys.exit()  
            break

        keyCode = cv2.waitKey(1) & 0xFF
        # Stop the program on the ESC key
        if keyCode == 27:

            break

        # INSERIR VALORES AQUI
        (curr_position, 
        infer_trigger, 
        check_trigger) = mov_detector(
                                    gpio_sensor=gpio_sensor, 
                                    cm_hole=cm_hole, 
                                    disk_hole_qtt=disk_hole_qtt, 
                                    height=height,
                                    start_photo_inference=start_infer_photo, 
                                    start_photo_check=start_check_photo, 
                                    spray_line1=blue_pins, 
                                    spray_line2=red_pins) 

        # print('[WEEDS] Position:', curr_position,', Infer Trigger:', infer_trigger,', Check Trigger:', check_trigger)
        
        (frame, 
        photo_name, 
        box_map) = camera_inference(
                                    frame=infer_photo, 
                                    path_photo=path_to_photos, 
                                    path_bbox=path_to_bbox_photos,
                                    save_photo_bbox=True, 
                                    take_photo=infer_trigger, 
                                    photo_position_ref=curr_position, 
                                    model=detection_model, 
                                    path_to_csv=csv_file, 
                                    cut_width=value_to_cut_usb_width_photo, 
                                    reshape_photo=reshape_value)

        (resized_bbox_map, 
        calibrated_bbox_map) = resize_adjust_bbox_map(
                                                    bbox_map=box_map, 
                                                    sprayers_qtt=sprayers_per_line, 
                                                    disk_hole_num=disk_hole_qtt, 
                                                    adj_start=dif_calib_start, 
                                                    adj_end=dif_calib_end, 
                                                    photo_position_ref=curr_position,
                                                    show_map=False, 
                                                    phis_dist=dist_infer_spray, 
                                                    take_photo=infer_trigger, 
                                                    convertion_base=walked_positions)

        spray(box_to_print=box_to_print, 
            position=curr_position, 
            sprayer_blue=blue_dict, 
            sprayer_red=red_dict, 
            sleeping=sleep_time)

        if infer_trigger: 
            box_to_print = np.insert(calibrated_bbox_map,-1,box_to_print, axis=0)
            print('[WEEDS] len box to print ',len(box_to_print),'and shape ',box_to_print.shape)
            
        elif curr_position * cm_hole >= height:
            print('[WEEDS] len box to print ',len(box_to_print),'and shape ',box_to_print.shape)

        else:
            box_to_print = np.insert(calibrated_bbox_map,-1,box_to_print, axis=0)
    
            print('[WEEDS] len box to print ',len(box_to_print),'and shape ',box_to_print.shape)

        (check_resized_map, 
        check_photos_qtt) = check_spray(frame=check_photo, 
                                        save_check_photo=True, 
                                        trigger_photo=check_trigger, 
                                        path_check_photo=path_to_check_photos, 
                                        position=curr_position, 
                                        qqt_sprayer=sprayers_per_line, 
                                        phis_dist=dist_between_cameras, 
                                        convertion_base=walked_positions,
                                        cut_width=value_to_cut_csi_width_photo, 
                                        reshape_photo=reshape_value,
                                        count_photos=check_photos_qtt)

        # if check_trigger:

        #     (dif_calib_start, 
        #     dif_calib_end) = find_values_to_adjust_by_index(base_map=box_to_print, 
        #                                                     spray_map=check_resized_map,
        #                                                     range_photo_basis=check_photos_qtt, 
        #                                                     photo_resized_param=walked_positions,
        #                                                     phis_dist=dist_infer_spray)

        #     print(f'[WEEDS] Difference to calibrate the BEGINNING of the spray: {dif_calib_start}')
        #     print(f'[WEEDS] Difference to calibrate the END of the spray: {dif_calib_end}')
