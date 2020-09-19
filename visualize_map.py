#!/usr/bin/python3

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import cv2

map_path = '/PATHTOCSV/2020-08-03-bbox-modulo-01.csv'
# Each photo has 80 centimeters of height
# The length has to be inserted
# You will need to resize the 300 x 300 photo to the length and height of the real photo
height = 80 #cm
length = 120 #cm

def visualize_map(path=map_path, height_cm=height, length_cm=length, save_photo=True):

    class_info = ['dontcare','Short', 'Long','Cane']

    weed_map = pd.read_csv(path)
    
    photo_height_dim = weed_map['height'][0]
    photo_width_dim = weed_map['width'][0]

    weed_map['height photo'] = (weed_map['ymax'] - weed_map['ymin']) / photo_height_dim * height_cm
    weed_map['width photo'] = (weed_map['xmax'] - weed_map['xmin']) / photo_width_dim * length_cm
    weed_map['area in cm2'] = weed_map['height photo'] * weed_map['width photo']

    # The total distance traveled is the last position times the height
    max_distance = max(weed_map['position']) / 100 * height_cm
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

    # Renaming the indes
    for i in range(0,len(weed_info)):
            weed_info.rename(index={weed_info.index[i]: class_info[i+1]}, inplace=True)

    print(weed_info)

if __name__ == '__main__':

    visualize_map()
