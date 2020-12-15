import cv2
from cv2 import aruco
import numpy as np
band_size = 150

class Intersection:
    def __init__(self, corners, 
                noise_threshold = 5,
                dictionary = aruco.Dictionary_get(aruco.DICT_6X6_250),
                roi_size = 200,
                show_Image = False
                ):
        self.ids = corners

        # ArUco dictionary and default detector parameters
        self.dictionary = dictionary#aruco.Dictionary_get(aruco.DICT_6X6_250)
        self.parameters = aruco.DetectorParameters_create()

        self.roi_size = roi_size
        self.roi_shape = np.array([[0.0,0.0],[self.roi_size, 0.0],[ 0.0,self.roi_size],[self.roi_size, self.roi_size]])

        self.noise_threshold = noise_threshold

        self.show_Image = show_Image
        self.no_ref = True
        self.ref = 0

    def get_cornerPoint(self, ids, id, corners):
        index = np.squeeze(np.where(ids == id))
        point = np.squeeze(corners[index[0]])[0]
        return point


    def intersectionMonitor(self, frame):
        # detect all markers
        markerCorners, markerIds, rejectedCandidates = aruco.detectMarkers(frame, self.dictionary, parameters=self.parameters)

        
        if markerIds is None:
            print('Markers not detected')
            return -1

            
        # Check that all corners are present

        if all(x in markerIds for x in self.ids):

            roi_corners = np.array([
                self.get_cornerPoint(markerIds, self.ids[0], markerCorners), self.get_cornerPoint(markerIds, self.ids[1], markerCorners),
                self.get_cornerPoint(markerIds, self.ids[2], markerCorners), self.get_cornerPoint(markerIds, self.ids[3], markerCorners)
            ])

            # Get homography and warp image feed into roi
            h, status = cv2.findHomography(roi_corners, self.roi_shape)
            roi = cv2.warpPerspective(frame, h, (self.roi_size,self.roi_size))
            if self.show_Image:
                cv2.imshow("Region of interest raw", roi)

            # Reduce ROI to binary 2D matrix
            (thresh, roi) = cv2.threshold(roi, 127, 255, cv2.THRESH_BINARY)
            roi = roi[:,:,0]

            if self.no_ref and 94 in markerIds:
                self.ref = roi 
                self.no_ref = False
            else:

                # Calculate difference
                diff = cv2.subtract(self.ref, roi)
                print(np.average(diff))
                if self.show_Image:
                    cv2.imshow("Region of interest", roi)
                    cv2.imshow('Detected Objects', diff)

                if np.average(diff) < self.noise_threshold:
                    return 0
                else:
                    color = (0, 0, 0) 


                    frame = cv2.rectangle(frame, tuple(roi_corners[0]-80), tuple(roi_corners[3]+80), color, -1) 
                    # print(roi_corners)
                    roi_corners[0] = [roi_corners[0][0] - band_size, roi_corners[0][1] - band_size]
                    roi_corners[1] = [roi_corners[1][0] + band_size, roi_corners[1][1] - band_size]
                    roi_corners[2] = [roi_corners[2][0] - band_size, roi_corners[2][1] + band_size]
                    roi_corners[3] = [roi_corners[3][0] + band_size, roi_corners[3][1] + band_size]

                    # Get homography and warp image feed into roi
                    h, status = cv2.findHomography(roi_corners, self.roi_shape)
                    roi2 = cv2.warpPerspective(frame, h, (self.roi_size,self.roi_size))
                    markerCorners, markerIds, rejectedCandidates = aruco.detectMarkers(roi2, aruco.Dictionary_get(aruco.DICT_6X6_250), parameters=aruco.DetectorParameters_create())
                    if markerIds is not None:
                        print(markerIds)

                    if self.show_Image:
                        cv2.imshow("Region of interest 2", roi2)
                    # cv2.imshow("Region of interest 2", roi2)

                    return 1



        else:
            print('Not all markers detected')
            return -1