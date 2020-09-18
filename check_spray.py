#!/usr/bin/python3
import Jetson.GPIO as GPIO
from datetime import datetime
import numpy as np
import cv2

def check_spray(frame=0, 
                save_check_photo=True, 
                trigger_photo=False,
                path_check_photo=None, 
                position=0, 
                reshape_photo=300,
                convertion_base=0, 
                qqt_sprayer=0, 
                phis_dist=0, 
                cut_width=0,
                count_photos=0):
    
    # trigger_photo = 'check_photo' variable from mov_detect
    # check_check_photo_name = 'photo_name' variable from infer_camera_processing
    
    '''This function in going to take a photo from the sprayed weed and check if it 
    was sprayed correctly.
    count_photos: if it's the first photo, it will adjust the phisical distance for a first time.
    disk_hole_num: the quantity of holes in the rotary reader to be used to resize the lines
    convertion_base: This is the base to be used to count photos.

    Below are the step in this process:
    
    * Take a photo
    * Blur it
    * define which color we are going to filter, other colors are going to be dismissed
    
    '''

    print('[WEEDS] Taking photo of the sprayed map')
         
    if trigger_photo == False:
        
        resized_bbox_map = 0
        
    else:
        
        now = datetime.now()

        #Setting basis for filename
        period = [now.year, now.month, now.day, now.hour, now.minute, now.second]

        for idx, time in enumerate(period):
            if len(f'{time}') == 1:
                period[idx] = f'0{time}'
        photo_name = ''.join([str(x) for x in period])  

        # Cutting the width photo, so when resize it won't be weird (IF YOU WANT TO CENTRALIZE CUT IN BOTH SIDE, 
        # IF YOU DON'T CUT IN ONE SIDE AND MULTP. BY 2)
        # It also will put the infer camera and check camera on the same basis
        frame = frame[:,cut_width:frame.shape[1]]
        print('WIDTH AND HEIGHT AFTER CUT', frame.shape[0], frame.shape[1])  

        print('[WEEDS] CHECK PHOTO TRIGGERED')
        
        count_photos += 1 
        
        # This is going to be the base file to put the contours of the sprayed photos.
        sprayed_map = np.zeros((reshape_photo, reshape_photo), np.uint8)

        # HSV RANGE (RED AND BLUE)
        low = np.array([0, 0, 0])
        high = np.array([27, 255, 255])

        frame = cv2.resize(frame, (reshape_photo,reshape_photo))

        # Flipping image
        frame = cv2.flip(frame, 1)

        image = cv2.GaussianBlur(frame, (9,9), 1)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(image, low, high)
        image = cv2.bitwise_and(image, image, mask=mask)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        contours, hierarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, 
                                                cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:

            area = cv2.contourArea(cnt)

            if area > 1000:

                accuracy = cv2.arcLength(cnt, True) * 0.015
                approx = cv2.approxPolyDP(cnt, accuracy, True)
                hull = cv2.convexHull(approx, True)
                final = cv2.drawContours(image, [hull], 0, (255,0,0), -1)
                sprayed_map = cv2.drawContours(sprayed_map, [hull], 0, 50, -1)

        # Splitting the bounding boxes according to the spray qtt
        cols = np.array(np.split(sprayed_map, qqt_sprayer, axis=1))

        #Getting the max values of each cols
        max_value_col = np.array([np.max(x, axis=1) for x in cols]).T

        #Splitting the bounding boxes according to the holes numbers in the disk
        lines = np.array(np.split(max_value_col, convertion_base, axis=0))

        #Getting the max values of each cols
        max_value_line = np.array([np.max(x, axis=0) for x in lines])
        
        #New bounding Box (this is the basis to compare with the sprayed)
        # if count_photos == 1:
        #     adj_distance = np.zeros([phis_dist, qqt_sprayer],np.uint8)
        #     resized_bbox_map = np.insert(max_value_line.astype(np.uint8), 
        #                                     -1, adj_distance, axis=0)
        # else:
        resized_bbox_map = max_value_line.astype(np.uint8)
        print('[WEEDS] Check Photos Count', count_photos)

        if save_check_photo:

            # saving the photo for later analysis
            normal_photo_name = path_check_photo + f'{photo_name}.jpg'
            #bbox_photo_name = path_check_photo + f'{photo_name}-Map.jpg'

            cv2.imwrite(normal_photo_name, frame)
            # saving with boxes
           # cv2.imwrite(bbox_photo_name, final)  
        
    return resized_bbox_map, count_photos  

if __name__ == '__main__':

    check_spray()