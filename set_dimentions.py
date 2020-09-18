#!/usr/bin/python3

import numpy as np

def set_dimentions(desired_height=80, 
                    desired_width=120, 
                    infer_stick=50, 
                    check_stick=90, 
                    equip_depth=105):

    # TO DO: CALCULATE THE DISTANCE BETWEEN THE MODULES ACCORDING TO THE HEIGHT OF EACH CAMERAS

    ''' Given the desired height of the camera, it will return the depth that the CSI and USB 
    cameras must have and also the values to be used to cut the photo taken to have de desired 
    width with an aditional margin of 10%'''
    
    # Measurements done for USB camera (height and width)
    usb_height_basis = np.arctan(29.25/77) 
    usb_width_basis = np.arctan(53.25/77) 
    # Defining the USB depth
    usb_cam_depth = desired_height / (np.tan(usb_height_basis) * 2)

    # The result is the width according to the USB depth
    usb_width = np.tan(usb_width_basis) * usb_cam_depth * 2

    # Return the difference to be used to cut the photo (width)
    # We will use half of the result to cut it from the left and right of the photo
    # We will also ADD 10% for security margin
    usb_width_dif = int(((usb_width - desired_width)) / 1.1)
    print(f'[WEEDS] To obtain a height of {desired_height} cm, put the USB depth at {round(usb_cam_depth,2)} cm')
    print(f'[WEEDS] The resultant width for the USB camera was {int(usb_width)} cm')
    print(f'[WEEDS] Use the value of {usb_width_dif} cm to cut the left side of the USB photos before resize it\n')


    # Measurements done for CSI camera (height and width)
    csi_height_basis = np.arctan(20.5/77) 
    csi_width_basis = np.arctan(35.375/77)

    csi_cam_depth = desired_height / (np.tan(csi_height_basis) * 2)

    # The result is the width according to the CSI depth
    csi_width = np.tan(csi_width_basis) * csi_cam_depth * 2

    # Return the difference to be used to cut the photo (width)
    # We will use half of the result to cut it from the left and right of the photo
    # We will also ADD 10% for security margin
    csi_width_dif = int(((csi_width - desired_width)) / 1.1)
    print(f'[WEEDS] To obtain a height of {desired_height} put the CSI depth at {round(csi_cam_depth,2)} cm')
    print(f'[WEEDS] The resultant width for the CSI camera was {int(csi_width)} cm')
    print(f'[WEEDS] Use the value of {csi_width_dif} cm to cut the left side of the CSI photos before resize it\n')

    # Measuring the equipment size according to the angle of each stike (infer and check sticks - they'll be with the same size)
    usb_depth_dif = np.abs(equip_depth - usb_cam_depth)
    csi_depth_dif = np.abs(equip_depth - csi_cam_depth)
    # Calculating the angle of the right angle, I have the hypotenuse (stick size) and one cateto (depth dif)
    new_usb_stick_size = np.sqrt(infer_stick**2 - usb_depth_dif**2)
    new_csi_stick_size = np.sqrt(check_stick**2 - csi_depth_dif**2)
    print(f'[WEEDS] The distance from the beginning to the end in stick of the USB camera is {round(new_usb_stick_size,2)} cm')
    print(f'[WEEDS] The distance from the beginning to the end in stick of the CSI camera is {round(new_csi_stick_size,2)} cm')

    return usb_width_dif, csi_width_dif, new_usb_stick_size, new_csi_stick_size

if __name__ == '__main__':

    set_dimentions()