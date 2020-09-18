#!/usr/bin/python3

import csv
import cv2
from datetime import datetime
import jetson.utils
import jetson.inference
import numpy as np

def camera_inference(frame=0, 
                    path_photo=None, 
                    path_bbox=None, 
                    save_photo_bbox=True,
                    path_to_csv=0, 
                    reshape_photo=0,
                    take_photo=False, 
                    photo_position_ref=0, 
                    model=None, 
                    cut_width=0, 
                    convertion_base=0):
    
    # photo_position_ref == 'curr_position' from mov_detect
    # take_photo = 'infer_trigger' from mov_detect
  
    # Opening the camera
    if take_photo == False:

        frame = 0
        photo_name = 0
        print('[WEEDS] No map to Create')
        box_map = 0
        
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
        
        # Flipping image
        frame = cv2.flip(frame, 1)
        
        # saving the photo for later analysis
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

            #criando a base para o csv
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
        cv2.imwrite(file_box, conv2)  
        cv2.imshow('INFERENCE', conv2)

        print('TOTAL INFERENCE TIME (LOAD CAMERA, INFER, SAVE IMAGES:', datetime.now()-now)
 
    return frame, photo_name, box_map

if __name__ == '__main__':

    infer_camera()