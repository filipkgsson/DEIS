import cv2
from cv2 import aruco
import numpy as np
import math

# Open camera feed from GPS camera
feed = cv2.VideoCapture("rtsp://192.168.1.2:554/axis-media/media.amp") 

# Initialize ArUco dictionary and default detector parameters
dictionary = aruco.Dictionary_get(aruco.DICT_6X6_250)
parameters = aruco.DetectorParameters_create()

robotID = 42

def get_Centroid(corners):
    length = corners.shape[0]
    sum_x = np.sum(corners[:, 0])
    sum_y = np.sum(corners[:, 1])
    return sum_x/length, sum_y/length

def get_Direction(point):
    x = point[0]+0.0001
    y = point[1]#
    theta = math.atan(y/x)
    #print(math.degrees(theta))
    if x >= 0 and y >= 0:
        return math.degrees(theta)
    elif x >= 0 and y <= 0:
        return math.degrees(theta) + 360
    elif x <= 0 and y <= 0:
        return math.degrees(theta) + 180
    else:
        return math.degrees(theta) + 180

def get_gps():
    hasFrame, frame = feed.read()

    markerCorners, markerIds, rejectedCandidates = aruco.detectMarkers(frame, dictionary, parameters=parameters)
    if markerIds is None:
        #print('Markers not detected')
        return (-1, -1), -1


    # Check that all corners are present
    if robotID in markerIds:
        index = np.squeeze(np.where(markerIds==robotID))[0]
        if index.shape:
            #print('Multiple Robots detected')
            return (-1, -1), -1
        center = get_Centroid(markerCorners[index][0])
        orientation = get_Direction(markerCorners[index][0][0]- markerCorners[index][0][1])

        return center, orientation
    else:
        #print('Robot not detected')
        return (-1, -1), -1
