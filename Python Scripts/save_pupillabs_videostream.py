# This code helps in saving the capture data as .avi files
# To understand the code make sure to start from the the main function
# To change the name of the subject just update the "name" variable
# Author: Chinmay Chinara
######################################################################################################################

from __future__ import print_function

# package for using Pupil Labs camera that are on UVC (Universal Video Class)
# for more details: https://en.wikipedia.org/wiki/USB_video_device_class
# for details specific to pupil labs camera: https://github.com/pupil-labs/pupil-docs and https://docs.pupil-labs.com/
import uvc

# import opencv module
import cv2

#import numpy module
import numpy as np

# import time module to check for time between different code chuncks
from time import time,sleep

try:
    # import multiprocessing package to make sure all the three cameras start in sync
    # the multiprocessing module allows the programmer to fully leverage multiple processors on a given machine
    # for more details: https://docs.python.org/3/library/multiprocessing.html
    from multiprocessing import Process,forking_enable,freeze_support
except ImportError:
    try:
        # python3
        from multiprocessing import Process,set_start_method,freeze_support
        def forking_enable(_):
            set_start_method('spawn')
    except ImportError:
        # python2 macos
        from billiard import Process,forking_enable,freeze_support

# get the list of devices that are connected in uvc platform
dev_list =  uvc.device_list()

# name of the subject
name = 'aakash'

# Define the codec and create VideoWriter object
# Videowriter class for windows just supports DIVX codec currently
fourcc = cv2.VideoWriter_fourcc(*'DIVX')
out_left_eye = cv2.VideoWriter(name + '_left_eye.avi',fourcc, 60.0, (640,480))
out_right_eye = cv2.VideoWriter(name + '_right_eye.avi',fourcc, 60.0, (640,480))
out_mouth = cv2.VideoWriter(name + '_mouth.avi',fourcc, 60.0, (640,480))

def my_name(i,title,mode=(640,480,120),format='bgr',bandwidth_factor=1.3):
    # get the ID of the camera and define it as an object
    cap = uvc.Capture(dev_list[i]['uid'])

    # set the bandwidth factor
    # to know more about what it is https://github.com/pupil-labs/pupil-docs/blob/master/developer-docs/usb-bandwidth-sync.md
    cap.bandwidth_factor = bandwidth_factor
    cap.frame_mode = mode

    while True:
        # get the ID of the camera and define it as an object
        frame = cap.get_frame_robust()
        data = frame.img

        if title == 'LEFT EYE CAPTURE':
            # vertical flip just to orient the video in the right view
            data = cv2.flip(data, 1)

            out_left_eye.write(data)
            cv2.imshow(title, data)
            cv2.moveWindow(title, 60, 0)

        if title == 'RIGHT EYE CAPTURE':
            # horizontal flip just to orient the video in the right view
            data = cv2.flip(data, 0)

            out_right_eye.write(data)
            cv2.imshow(title, data)
            cv2.moveWindow(title, np.size(data, 1) + 70, 0)

        if title == 'MOUTH CAPTURE':
            # horizontal flip just to orient the video in the right view
            data = cv2.flip(data, 0)

            out_mouth.write(data)
            cv2.imshow(title, data)
            cv2.moveWindow(title, int((np.size(data, 1) / 2)+60), np.size(data, 0) + 40)

        k = cv2.waitKey(1)
        if k == 27:
            cv2.destroyAllWindows()
            exit(0)

# the main code starts here
if __name__ == '__main__':
    freeze_support()
    forking_enable(0)

    # find the pupil labs cameras and their device IDs
    print('\n')
    leye_index = 0
    reye_index = 0
    mouth_index = 0
    count = 0

    # this logic helps in detecting and labeling the cameras based on their IDs
    for i in range(len(dev_list)):
        if dev_list[i]['manufacturer'] == 'Pupil Cam1 ID0':
            if(reye_index == 0):
                count = count + 1
                reye_index = i
                print('device_list index: ' + str(i)
                              + ' --> Right eye camera found with manufacturer id: '
                              + dev_list[i]['manufacturer'])
            else:
                count = count + 1
                mouth_index = i
                print('device_list index: ' + str(i)
                      + ' --> Mouth camera found with manufacturer id: '
                      + dev_list[i]['manufacturer'])

        elif dev_list[i]['manufacturer'] == 'Pupil Cam1 ID1':
            count = count + 1
            leye_index = i
            print('device_list index: ' + str(i)
                  + ' --> Left eye camera found with manufacturer id: '
                  + dev_list[i]['manufacturer'])
        else:
            print('device_list index: ' + str(i)
                          + ' --> No camera found, manufacturer id: '
                          + dev_list[i]['manufacturer'])

    # if all the three cameras are not found then exit the program
    print('\n')
    if(count != 3):
        print('All the three cameras are not connected...')
        print('Check connection and retry running !!!')
        exit(0)

    print(reye_index)
    print(mouth_index)
    print(leye_index)
    p0 = Process(target=my_name, args=(reye_index, 'RIGHT EYE CAPTURE', (640, 480, 120), 'gray'))
    p1 = Process(target=my_name,args=(leye_index,'LEFT EYE CAPTURE',(640,480,120),'gray'))
    p2 = Process(target=my_name,args=(mouth_index,'MOUTH CAPTURE',(640,480,120),'gray'))

    # start the multiprocessing of all the cameras
    # https://github.com/pupil-labs/pupil-docs/blob/master/developer-docs/usb-bandwidth-sync.md
    p0.start()
    p1.start()
    p2.start()