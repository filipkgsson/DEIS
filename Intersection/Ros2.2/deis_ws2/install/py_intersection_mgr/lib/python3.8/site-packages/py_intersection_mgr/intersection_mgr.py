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
from custom_interfaces.msg import Int

from std_msgs.msg import String


import cv2
from cv2 import aruco
import numpy as np

import sys
import traceback
import tellopy
import av
import time

# OpenCV Camera Feed
#cap = cv2.VideoCapture("rtsp://192.168.1.2:554/axis-media/media.amp") 

drone = tellopy.Tello()

go = [1,1]
class Intersection:
    def __init__(self, corners, id,
                noise_threshold = 10,
                dictionary = aruco.Dictionary_get(aruco.DICT_6X6_250),
                roi_size = 170,
                ):
        self.ids = corners
        self.id = id
        # ArUco dictionary and default detector parameters
        self.dictionary = dictionary#aruco.Dictionary_get(aruco.DICT_6X6_250)
        self.parameters = aruco.DetectorParameters_create()

        self.roi_size = roi_size
        self.roi_shape = np.array([[0.0,0.0],[self.roi_size, 0.0],[ 0.0,self.roi_size],[self.roi_size, self.roi_size]])

        self.noise_threshold = noise_threshold

        self.no_ref = True
        self.ref = 0
        self.band_size = 150
        

    def get_cornerPoint(self, ids, id, corners):
        index = np.squeeze(np.where(ids == id))
        point = np.squeeze(corners[index[0]])[0]
        return point


    def get_Status(self, frame, markerCorners, markerIds):
        # detect all markers
        #markerCorners, markerIds, rejectedCandidates = aruco.detectMarkers(frame, self.dictionary, parameters=self.parameters)

        global go 

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

            if self.no_ref and 94 in markerIds:
                self.ref = roi 
                self.no_ref = False
                print('Reference generated')
                return -1
                
            else:

                # Calculate difference
                diff = cv2.subtract(self.ref, roi)

                if np.average(diff) < self.noise_threshold:
                    #minimal_publisher2.publish_Status(1)
                    go[self.id] = 1
                    return 0
                else:

                    color = (0, 0, 0) 
                    frame = cv2.rectangle(frame, tuple(roi_corners[0]-65), tuple(roi_corners[3]+65), color, -1) 
                    # print(roi_corners)
                    roi_corners[0] = [roi_corners[0][0] - self.band_size, roi_corners[0][1] - self.band_size]
                    roi_corners[1] = [roi_corners[1][0] + self.band_size, roi_corners[1][1] - self.band_size]
                    roi_corners[2] = [roi_corners[2][0] - self.band_size, roi_corners[2][1] + self.band_size]
                    roi_corners[3] = [roi_corners[3][0] + self.band_size, roi_corners[3][1] + self.band_size]

                    # Get homography and warp image feed into roi
                    h, status = cv2.findHomography(roi_corners, self.roi_shape)
                    roi2 = cv2.warpPerspective(frame, h, (self.roi_size,self.roi_size))
                    markerCorners, markerIds, rejectedCandidates = aruco.detectMarkers(roi2, self.dictionary, parameters=self.parameters)
                                            

                    if markerIds is not None:
                        #print(markerIds)
                        if 42 in markerIds:
                            print('stop')
                            go[self.id] = 0
                            #minimal_publisher2.publish_Status(0)



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


# class MinimalPublisher2(Node):

#     def __init__(self):
#         super().__init__('minimal_publisher')
#         self.publisher_ = self.create_publisher(Int, 'i42', 10)

        
#     def publish_Status(self, status):
#         msg = Int()
#         msg.data = status
#         self.publisher_.publish(msg)
#         print(status)
#         #self.get_logger().info('"%s"' % msg.data)

class MinimalPublisher2(Node):

    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'i42', 10)

        
    def publish_Status(self, status):
        msg = String()
        msg.data = '%d' % status
        self.publisher_.publish(msg)
        print(status)
        #self.get_logger().info('"%s"' % msg.data)

        



def main(args=None):

    # Initialize Node
    rclpy.init(args=args)
    global minimal_publisher2
    global go 

    # Initialize Publisher
    minimal_publisher = MinimalPublisher()
    minimal_publisher2 = MinimalPublisher2()

    # Initialize intersections
    intersection_1 = Intersection([1,2,3,4],0)       
    intersection_2 = Intersection([91,92,93,94],1)       

    dictionary = aruco.Dictionary_get(aruco.DICT_6X6_250)
    parameters = aruco.DetectorParameters_create()

    try:
        drone.connect()
        drone.wait_for_connection(60.0)

        retry = 3
        container = None
        while container is None and 0 < retry:
            retry -= 1
            try:
                container = av.open(drone.get_video_stream())
            except av.AVError as ave:
                print(ave)
                print('retry...')

        # skip first 300 frames
        frame_skip = 300
        drone.takeoff()
        time.sleep(10)

        drone.up(30)
        time.sleep(2)
        drone.up(0)

        while True:

          for frame in container.decode(video=0):
                if 0 < frame_skip:
                    frame_skip = frame_skip - 1
                    continue
                start_time = time.time()
                image = cv2.cvtColor(np.array(frame.to_image()), cv2.COLOR_RGB2BGR)
                #cv2.imshow('Original', image)

                cv2.waitKey(1)
                if frame.time_base < 1.0/60:
                    time_base = 1.0/60
                else:
                    time_base = frame.time_base
                frame_skip = int((time.time() - start_time)/time_base)

                markerCorners, markerIds, rejectedCandidates = aruco.detectMarkers(image, dictionary, parameters=parameters)
                # Check intersections and publish stated
                minimal_publisher.publish_Status([intersection_1.get_Status(image,  markerCorners, markerIds),0])
      
                if 0 in go:
                    minimal_publisher2.publish_Status(0)
                else:
                    minimal_publisher2.publish_Status(1)

    except (Exception, KeyboardInterrupt, SystemExit):
        drone.land()
        drone.quit()
        cv2.destroyAllWindows()
        raise


    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
