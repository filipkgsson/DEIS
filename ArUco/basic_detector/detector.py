import cv2
from cv2 import aruco
import numpy as np
import math

# Open camera feed from GPS camera
cap = cv2.VideoCapture("rtsp://192.168.1.2:554/axis-media/media.amp") 
#cap = cv2.VideoCapture(0)

# Initialize ArUco dictionary and default detector parameters
dictionary = aruco.Dictionary_get(aruco.DICT_6X6_250)
parameters = aruco.DetectorParameters_create()

#### main ####
while cv2.waitKey(1) < 0:
    try:
        # get video frame
        hasFrame, frame = cap.read()

        # Detect markers
        markerCorners, markerIds, rejectedCandidates = aruco.detectMarkers(frame, dictionary, parameters=parameters)

        print(np.squeeze(np.where(markerIds==11)))
        #print(markerCorners)
        # Check if markers are detected and draw them on frame
        if markerIds is not None:
            frame = aruco.drawDetectedMarkers(frame, markerCorners, markerIds)

        # Show video Feed
        cv2.imshow("Camera feed", frame)

    except Exception as inst:
        print(inst)


cv2.destroyAllWindows()