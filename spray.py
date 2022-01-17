#!/usr/bin/python3

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import cv2

def visualize_map(path='', height_cm=80, length_cm=120, save_photo=True, cm_hole=0):
    
    ''' 
    By default each photo has 80 centimeters of height and 120 cm of lenght, you can change it to the desired
    photo dimentions, it has to have the real dimention taken in the photo.
    You will need to resize the 300 x 300 photo to the length and height of the real photo
    Parameters:
            path: The path for the CSV file to be visualized
            height_cm: The desired height of the detected object
            lenght_cm: The desired length of the detected object
            save_photo: boolean, if True it will save a simple image of the detections in the field.
            cm_hole: Information related to each step to convert the values from position to cm
    '''
    class_info = ['dontcare','Short', 'Long','Cane']

    weed_map = pd.read_csv(path)
    
    photo_height_dim = weed_map['height'][0]
    photo_width_dim = weed_map['width'][0]

    # Resizing the photo dimentions to the desired cm
    weed_map['height photo'] = (weed_map['ymax'] - weed_map['ymin']) / photo_height_dim * height_cm
    weed_map['width photo'] = (weed_map['xmax'] - weed_map['xmin']) / photo_width_dim * length_cm
    
    # Getting the total area
    weed_map['area in cm2'] = weed_map['height photo'] * weed_map['width photo']

    # The total distance traveled is the last position times the height
    max_distance = max(weed_map['position']) * cm_hole / 100 * height_cm
    print(f'\n The distance traveled was {max_distance/100} meters \n')

    base_map = np.zeros((int(photo_width_dim * max(weed_map['position']/100)),
                        photo_height_dim), np.uint8)

    for i in range(len(weed_map)):
        
        position_reference = int(max(weed_map['position']/100) - weed_map['position'].iloc[i] / 100)
        class_names = class_info[weed_map['class'].iloc[i]]
        
        # Drawing bounding box rectangle
        base_map = cv2.rectangle(base_map, 
                                (int(weed_map['xmin'].iloc[i]), int(weed_map['ymin'].iloc[i] + position_reference * 300)),
                                (int(weed_map['xmax'].iloc[i]), int(weed_map['ymax'].iloc[i] + position_reference * 300)),
                                int(weed_map['class'].iloc[i] * 50), -1)
        
        # Drawing an external rectangle
        base_map = cv2.rectangle(base_map, 
                                (int(weed_map['xmin'].iloc[i]), int(weed_map['ymin'].iloc[i] + position_reference * 300)),
                                (int(weed_map['xmax'].iloc[i]), int(weed_map['ymax'].iloc[i] + position_reference * 300)),
                                int(weed_map['class'].iloc[i] * 60), 2)    
        # Class text
        cv2.putText(base_map, 
                    class_names, 
                    (int(weed_map['xmin'].iloc[i]), int(weed_map['ymin'].iloc[i] + position_reference * 300) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1, 
                    int(weed_map['class'].iloc[i] * 50),
                    2)
        
        # Drawing a line to separate each photo
        base_map = cv2.rectangle(base_map, 
                                (0, int(0 + position_reference * 300)),
                                (300, int(300 + position_reference * 300)), 50, 2)

    # plt.figure(figsize=(10,40))
    # plt.imshow(base_map)
    # plt.show()

    if save_photo:
        plt.imsave('map.jpg', base_map)

    weed_info = pd.DataFrame()
    weed_info['Weeds Detected'] = weed_map.groupby('class')['class'].count()
    weed_info['Mean Area cm2'] = round(weed_map.groupby('class').mean()['area in cm2'],2)
    weed_info['Total Area cm2'] = weed_map.groupby('class').sum()['area in cm2']

    # Renaming the index
    for i in range(0,len(weed_info)):
            weed_info.rename(index={weed_info.index[i]: class_info[i+1]}, inplace=True)

    print(weed_info)
