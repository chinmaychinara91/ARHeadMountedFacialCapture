# This code handles the client part of the video stream/data transfer from
# Pupil Labs' Cameras to HoloLens / Unity
# To understand the code make sure to start from the the main function
# Author: Chinmay Chinara
######################################################################################################################

from __future__ import print_function

# package for using Pupil Labs camera that are on UVC (Universal Video Class)
# for more details: https://en.wikipedia.org/wiki/USB_video_device_class
# for details specific to pupil labs camera: https://github.com/pupil-labs/pupil-docs and https://docs.pupil-labs.com/
import uvc

# import opencv module
import cv2

# import package for raw TCP/IP sockets
import socket

#import numpy module
import numpy as np

# import time module to check for time between different code chuncks
from time import time,sleep

try:
    from multiprocessing import reduction,Process,forking_enable,freeze_support
except ImportError:
    try:
        # python3
        from multiprocessing import Process,set_start_method,freeze_support
        def forking_enable(_):
            set_start_method('spawn')
    except ImportError:
        # python2 macos
        from billiard import Process,forking_enable,freeze_support

# configure the TCP IP host and port
# sending every camera feed through a separate socket
TCP_IP = '10.1.6.39' # local ip of the server used for connection
# TCP_PORT1 = 5000
TCP_PORT2 = 5001
# TCP_PORT3 = 5002
TCP_PORT4 = 5003
# TCP_PORT5 = 5004
TCP_PORT6 = 5005

# sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock5 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock6 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# get the list of devices that are connected in uvc platform
dev_list =  uvc.device_list()
# print(dev_list)

# function that defines the entore capture process
def my_name(i,title, mode=(640,480,60), format = 'gray', bandwidth_factor=1.3):
    # get the ID of the camera and define it as an object
    cap = uvc.Capture(dev_list[i]['uid'])

    # set the bandwidth factor
    # to know more about what it is https://github.com/pupil-labs/pupil-docs/blob/master/developer-docs/usb-bandwidth-sync.md
    cap.bandwidth_factor = bandwidth_factor

    # set the resolution of the capture
    cap.frame_mode = mode

    # logic to select the correct server to access the camera of interest
    if title == 'LEFT EYE CAPTURE':
        # sock1.connect((TCP_IP, TCP_PORT1))
        sock2.connect((TCP_IP, TCP_PORT2))
        print(title)
    if title == 'RIGHT EYE CAPTURE':
        # sock3.connect((TCP_IP, TCP_PORT3))
        sock4.connect((TCP_IP, TCP_PORT4))
        print(title)
    if title == 'MOUTH CAPTURE':
        # sock5.connect((TCP_IP, TCP_PORT5))
        sock6.connect((TCP_IP, TCP_PORT6))
        print(title)

    # title = cap.name + ' - ' + str(mode) + ' - ' + format
    while True:
        # capture every frame from the video
        frame = cap.get_frame_robust()
        data = frame.img

        # encoding done in order to adjust the quality of the frames that needs to be transmitted
        # be default it is it can range from 0 to 100, 100 being the highest quality
        # curently being transmitted at 55% compression
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 45]

        if title == 'LEFT EYE CAPTURE':
            # vertical flip just to orient the video in the right view
            data = cv2.flip(data, 1)

            # encode the image as a jpg compressed before transmission
            result, imgencode = cv2.imencode('.jpg', data, encode_param)

            data = np.array(imgencode)
            stringData = data.tostring()
            str1 = str(len(stringData)).ljust(16)
            # sock1.send(str1.encode())  # size of the data
            sock2.send(stringData)  # the data
            decimg = cv2.imdecode(data, 1)
            cv2.imshow('CLIENT ' + title, decimg)  # leye
            cv2.moveWindow('CLIENT ' + title, 0, np.size(decimg, 0) + 40)

        if title == 'RIGHT EYE CAPTURE':
            # horizontal flip just to orient the video in the right view
            data = cv2.flip(data, 0)

            # encode the image as a jpg compressed before transmission
            result, imgencode = cv2.imencode('.jpg', data, encode_param)

            data = np.array(imgencode)
            stringData = data.tostring()
            str2 = str(len(stringData)).ljust(16)
            # sock3.send(str2.encode())  # size of the data
            sock4.send(stringData)  # the data
            decimg = cv2.imdecode(data, 1)
            cv2.imshow('CLIENT ' + title, decimg)  # reye
            cv2.moveWindow('CLIENT ' + title, np.size(decimg, 1) + 10, np.size(decimg, 0) + 40)

        if title == 'MOUTH CAPTURE':
            # horizontal flip just to orient the video in the right view
            data = cv2.flip(data, 0)

            # encode the image as a jpg compressed before transmission
            result, imgencode = cv2.imencode('.jpg', data, encode_param)

            data = np.array(imgencode)
            stringData = data.tostring()
            str3 = str(len(stringData)).ljust(16)
            # sock5.send(str3.encode())  # size of the data
            sock6.send(stringData)  # the data
            decimg = cv2.imdecode(data, 1)
            cv2.imshow('CLIENT ' + title, decimg)  # reye
            cv2.moveWindow('CLIENT ' + title, 2 * np.size(decimg, 1) + 20, np.size(decimg, 0) + 40)

        k = cv2.waitKey(1)
        if k == 27:
            cv2.destroyAllWindows()
            sock.close()
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

    p0 = Process(target=my_name, args=(leye_index, 'LEFT EYE CAPTURE', (640, 480, 60), 'gray', 1.3))
    p1 = Process(target=my_name, args=(reye_index, 'RIGHT EYE CAPTURE', (640, 480, 60), 'gray', 1.3))
    p2 = Process(target=my_name, args=(mouth_index, 'MOUTH CAPTURE', (640, 480, 60), 'gray', 1.3))

    # start the multiprocessing of all the cameras
    # https://github.com/pupil-labs/pupil-docs/blob/master/developer-docs/usb-bandwidth-sync.md
    p0.start()
    p1.start()
    p2.start()