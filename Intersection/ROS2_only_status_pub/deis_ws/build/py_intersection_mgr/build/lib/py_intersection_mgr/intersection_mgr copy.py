# Copyright 2016 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import rclpy
from rclpy.node import Node
from custom_interfaces.msg import IntList

import cv2
from cv2 import aruco
import numpy as np

# OpenCV Camera Feed
cap = cv2.VideoCapture("rtsp://192.168.1.2:554/axis-media/media.amp") 

class Intersection:
    def __init__(self, corners, 
                noise_threshold = 1,
                dictionary = aruco.Dictionary_get(aruco.DICT_6X6_250),
                roi_size = 50,
                ):
        self.ids = corners

        # ArUco dictionary and default detector parameters
        self.dictionary = dictionary#aruco.Dictionary_get(aruco.DICT_6X6_250)
        self.parameters = aruco.DetectorParameters_create()

        self.roi_size = roi_size
        self.roi_shape = np.array([[0.0,0.0],[self.roi_size, 0.0],[ 0.0,self.roi_size],[self.roi_size, self.roi_size]])

        self.noise_threshold = noise_threshold

        self.no_ref = True
        self.ref = 0

    def get_cornerPoint(self, ids, id, corners):
        index = np.squeeze(np.where(ids == id))
        point = np.squeeze(corners[index[0]])[0]
        return point


    def get_Status(self, frame, markerCorners, markerIds):
        # detect all markers
        #markerCorners, markerIds, rejectedCandidates = aruco.detectMarkers(frame, self.dictionary, parameters=self.parameters)

        
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

            # Reduce ROI to binary 2D matrix
            (thresh, roi) = cv2.threshold(roi, 127, 255, cv2.THRESH_BINARY)
            roi = roi[:,:,0]

            if self.no_ref:
                self.ref = roi 
                self.no_ref = False
                print('Reference generated')
                return -1
                
            else:

                # Calculate difference
                diff = cv2.subtract(self.ref, roi)

                if np.average(diff) < self.noise_threshold:
                    return 0
                else:
                    return 1

        else:
            print('Not all markers detected')
            return -1


class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(IntList, 'intersection', 10)

        
    def publish_Status(self, status):
        msg = IntList()
        msg.data = status
        self.publisher_.publish(msg)
        print(status)
        #self.get_logger().info('"%s"' % msg.data)


def main(args=None):

    # Initialize Node
    rclpy.init(args=args)

    # Initialize Publisher
    minimal_publisher = MinimalPublisher()

    # Initialize intersections
    intersection_1 = Intersection([1,2,3,4])       
    intersection_2 = Intersection([91,92,93,94])       

    dictionary = aruco.Dictionary_get(aruco.DICT_6X6_250)
    parameters = aruco.DetectorParameters_create()

    # Read new frame
    while cv2.waitKey(1) < 0:
        try:
            # Get frame 
            hasFrame, frame = cap.read()

            markerCorners, markerIds, rejectedCandidates = aruco.detectMarkers(frame, dictionary, parameters=parameters)
            # Check intersections and publish stated
            minimal_publisher.publish_Status([intersection_1.get_Status(frame,  markerCorners, markerIds), intersection_2.get_Status(frame,  markerCorners, markerIds)])

        except (Exception, KeyboardInterrupt, SystemExit):
            cv2.destroyAllWindows()
            raise


    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
