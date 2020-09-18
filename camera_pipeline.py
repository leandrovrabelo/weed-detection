#!/usr/bin/python3
import cv2

def camera_pipeline(capture_width=1280, 
                capture_height=720,
                display_width=640, 
                display_height=360,
                framerate=120, 
                flip_method=0, 
                cam_type=None):

    pipeline = "nvarguscamerasrc ! video/x-raw(memory:NVMM), \
        width=(int)%d, height=(int)%d, format=(string)NV12, \
        framerate=(fraction)%d/1 ! nvvidconv flip-method=%d ! \
        video/x-raw, width=(int)%d, height=(int)%d, \
        format=(string)BGRx ! videoconvert ! \
        video/x-raw, format=(string)BGR ! appsink"%(capture_width, 
        capture_height, 
        framerate, 
        flip_method, 
        display_width,
        display_height)
    
    if cam_type == 'usb':
        print(f'Opening {cam_type} Camera')   
        cam = cv2.VideoCapture('/dev/video1')
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, capture_width)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, capture_height)
        cam.set(cv2.CAP_PROP_FPS, framerate)

    elif cam_type == 'csi':
        print(f'Opening {cam_type} Camera') 
        cam = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

    elif cam_type == 'cam':
        print(f'Opening {cam_type} Camera') 
        cam = cv2.VideoCapture(0)
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, capture_width)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, capture_height)

    else:
        print('Wrong Camera, parse (usb, csi or cam) parameters')
    return cam

if __name__ == '__main__':

    camera_pipeline()