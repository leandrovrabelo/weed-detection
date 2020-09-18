#!/usr/bin/python3

import numpy as np
from calibration import calibrate, find_values_to_adjust

def resize_adjust_bbox_map(bbox_map=0, 
                    sprayers_qtt=0, 
                    disk_hole_num=0, 
                    adj_start=0, 
                    adj_end=0, 
                    show_map=False, 
                    phis_dist=0, 
                    photo_position_ref=0,
                    take_photo=False, 
                    count_photos=0, 
                    convertion_base=0):
    # take_photo = 'infer_trigger' from mov_detect
    '''Resizing the bounding box to fit the sprayers quantities.
    After splitting the bounding box, the max values for each line will be considered.
    
    Params:
    -----------
    bbox_map: Bounding box to be resized
    adj_start: difference of the TURN ON sprayed values with the values that were 
                supposed to be sprayed.
    adj_end: difference of the TURN OFF sprayed values with the values that were 
                supposed to be sprayed.
    sprayers_qtt: Quantity of sprayers to print the information (two lines)
    show_map: bool, if True it will print the map on the notebook
    phis_dist: It's the phisical distance between the camera and the sprayers, it will correct the 
                initial values
    count_photos: if it's the first photo, it will adjust the phisical distance for a first time.
    disk_hole_num: the quantity of holes in the rotary reader to be used to resize the lines
    convertion_base: This is the base to be used to count photos.
    -----------
    return: new bounding box with RESIZED columns (this is the real basis)
    return: new bounding box with ADJUSTED columns (this is the basis to be sprayed)'''
    if take_photo:

        count_photos = int(photo_position_ref // convertion_base)

        #Splitting the bounding boxes according to the spray qtt
        cols = np.array(np.split(bbox_map, sprayers_qtt, axis=1))

        #Getting the max values of each cols
        max_value_col = np.array([np.max(x, axis=1) for x in cols]).T

        #Splitting the bounding boxes according to the holes numbers in the disk
        lines = np.array(np.split(max_value_col, convertion_base, axis=0))

        #Getting the max values of each cols
        max_value_line = np.array([np.max(x, axis=0) for x in lines])
        
        #New bounding Box (this is the basis to compare with the sprayed)
        # if count_photos == 1:
        #     adj_distance = np.zeros([phis_dist, sprayers_qtt],np.uint8)
        #     resized_bbox_map = np.insert(max_value_line.astype(np.uint8), 
        #                                     -1, adj_distance, axis=0)
        # else:
        resized_bbox_map = max_value_line.astype(np.uint8)

        print('[WEEDS] Photo number',count_photos)
        calibrated_bbox_map = calibrate(resized_bbox_map, 
                                        start=adj_start, 
                                        end=adj_end)

        print('[WEEDS] Resizing the Maps')

        if show_map:
            plt.imshow(resized_bbox_map)
            plt.show()

        return resized_bbox_map, calibrated_bbox_map 
    else:
        resized_bbox_map = np.zeros((1,sprayers_qtt), np.uint8)
        calibrated_bbox_map = np.zeros((1,sprayers_qtt), np.uint8)

        return resized_bbox_map, calibrated_bbox_map 

