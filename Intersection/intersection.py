import cv2
from cv2 import aruco
import numpy as np

class Intersection:
    def __init__(self, corners):
        self.ids = corners

        # ArUco dictionary and default detector parameters
        self.dictionary = aruco.Dictionary_get(aruco.DICT_6X6_250)
        self.parameters = aruco.DetectorParameters_create()

        self.roi_size = 200
        self.roi_shape = np.array([[0.0,0.0],[roi_size, 0.0],[ 0.0,roi_size],[roi_size, roi_size]])

        self.noise_threshold = 1

        self.show_Image = False
        self.noRef = True
        self.ref = 0

    def get_cornerPoint(self, id, corners):
        index = np.squeeze(np.where(self.ids == id))
        point = np.squeeze(corners[index[0]])[0]
        return point


    def intersectionMonitor(self, frame):
        # detect all markers
        markerCorners, markerIds, rejectedCandidates = aruco.detectMarkers(frame, dictionary, parameters=parameters)

        
        if markerIds is None:
            print('Markers not detected')
            return -1

            
        # Check that all corners are present
        if all(x in markerIds for x in ids):

            roi_corners = np.array([
                get_cornerPoint(markerIds, self.ids [0], markerCorners), get_cornerPoint(markerIds, self.ids [1], markerCorners),
                get_cornerPoint(markerIds, self.ids [2], markerCorners), get_cornerPoint(markerIds, self.ids [3], markerCorners)
            ])

            # Get homography and warp image feed into roi
            h, status = cv2.findHomography(roi_corners, roi_shape)
            roi = cv2.warpPerspective(frame, h, (roi_size,roi_size))
            if show_Image:
                cv2.imshow("Region of interest raw", roi)

            # Reduce ROI to binary 2D matrix
            (thresh, roi) = cv2.threshold(roi, 127, 255, cv2.THRESH_BINARY)
            roi = roi[:,:,0]

            if noRef:
                ref = roi 
                noRef = False
            else:

                # Calculate difference
                diff = cv2.subtract(ref, roi)

                if np.average(diff) < noise_threshold:
                    return 0
                else:
                    return 1

                if show_Image:
                    cv2.imshow("Region of interest", roi)
                    cv2.imshow('Detected Objects', diff)

        else:
            print('Not all markers detected')
            return -1