#!/usr/bin/python3

import csv
import cv2
from datetime import datetime
import jetson.utils
import jetson.inference
import numpy as np

def camera_inference(frame=None, 
                    path_photo=None, 
                    path_bbox=None, 
                    save_photo_bbox=True,
                    path_to_csv=0, 
                    reshape_photo=300,
                    take_photo=False, 
                    photo_position_ref=0, 
                    model=None, 
                    cut_width=0):
    '''
    This function is one of the most important of the project, it gets the picture taken from the field and
    do an inference to check for different kind of weeds.

    Parameters:
                frame: it's the picture of the field when the the trigger is activated
                path_photo: it's the path to save the image without bounding boxes
                path_bbox: it's the path to save the image with bounding boxes
                save_photo_bbox: boolean
                path_to_csv: it's the path to save the inference information in the csv file
                reshape_photo: the desired pixels to reshape the picture for inference, default is 300 pixels
                take_photo: boolean, if True the whole inference process will be done
                photo_position_ref: it's the current position when the photo was taken, 
                                    it will be used to save as a position information in the csv file
                model: it's the object detection model to do the inference
                cut_width: This is an information used to cut the picture before reshaping, it was used to put the
                inference camera (usb) in the same reference position of the CSI camera, there are some differences in 
                pixels resolutions when the cameras are in the same height.
    '''  
    
    if take_photo:

        now = datetime.now()
        #Setting basis for filename
        period = [now.year, now.month, now.day, now.hour, now.minute, now.second]

        for idx, time in enumerate(period):
            if len(f'{time}') == 1:
                period[idx] = f'0{time}'
        photo_name = ''.join([str(x) for x in period])  

        # Cutting the width photo, so when resize it won't be weird (IF YOU WANT TO CENTRALIZE CUT IN BOTH SIDE, 
        # IF YOU DON'T WANT, CUT IN ONE SIDE AND MULTP. BY 2)
        # It also will put the infer camera and check camera on the same basis
        frame = frame[:,cut_width:frame.shape[1]]
        print('WIDTH AND HEIGHT AFTER CUT', frame.shape[0], frame.shape[1])  
        
        # Flipping image
        frame = cv2.flip(frame, 1)
        
        # saving the photo for later analysis, it's mandatory
        file_simple = path_photo + f'{photo_name}.jpg'
        cv2.imwrite(file_simple, frame)

        # Reshaping the image
        frame = cv2.resize(frame, (reshape_photo,reshape_photo))
        frame_rgba = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA).astype(np.float32)
        
        img = jetson.utils.cudaFromNumpy(frame_rgba)

        detections = model.Detect(img, 
                                reshape_photo, 
                                reshape_photo, 
                                "box,labels,conf")
                                
        # Converting back to RGB
        conv1 = jetson.utils.cudaToNumpy(img, reshape_photo, reshape_photo, 4)        
        conv2 = cv2.cvtColor(conv1, cv2.COLOR_RGBA2BGR).astype(np.uint8)

        for detection in detections:
            print('{detection}:', detection)

        #print out timing info
        model.PrintProfilerTimes()
        print(type(img))

        # CREATING BOX MAPS
        box_map = np.zeros([reshape_photo, reshape_photo], np.uint8)
        
        for i in range(len(detections)):
            box_map = cv2.rectangle(box_map, 
                                    (int(detections[i].Left), int(detections[i].Top)),
                                    (int(detections[i].Right), int(detections[i].Bottom)),
                                    detections[i].ClassID * 50,-1)

            #creating the base information for the csv file
            # TODO: check if the variable reshape_photo can be changed to img.shape[0] and img.shape[1]
            info_csv = [f'{photo_name[-22:]}.jpg', reshape_photo, reshape_photo, 
                        detections[i].ClassID, int(detections[i].Left), 
                        int(detections[i].Top), int(detections[i].Right), 
                        int(detections[i].Bottom), int(photo_position_ref)]

            with open(path_to_csv, 'a') as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow(info_csv)
        
        # saving the photo for later analysis
        file_box = path_bbox + f'{photo_name}.jpg'
        
        # saving with boxes
        if save_photo_bbox:
            cv2.imwrite(file_box, conv2)  
            cv2.imshow('INFERENCE', conv2)

        print('TOTAL INFERENCE TIME (LOAD CAMERA, INFER, SAVE IMAGES:', datetime.now()-now)
    
    else:
        print('[WEEDS] No map to Create')
        box_map = 0
        
 
    return box_map
