import sys
import traceback
import tellopy
import av
import numpy
import time

import cv2
from cv2 import aruco
import intersection as intersection


drone = tellopy.Tello()

# OpenCV Camera Feed
#cap = cv2.VideoCapture("rtsp://192.168.1.2:554/axis-media/media.amp") 
#cap = cv2.VideoCapture(0)

show_Video = True

intersection_1 = intersection.Intersection([1,2,3,4])
intersection_2 = intersection.Intersection([91,92,93,94])

#### main ####
def main(args=None):

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

        drone.up(20)
        time.sleep(2)
        drone.up(0)

        while True:

            for frame in container.decode(video=0):
                if 0 < frame_skip:
                    frame_skip = frame_skip - 1
                    continue
                start_time = time.time()
                image = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)
                #cv2.imshow('Original', image)

                cv2.waitKey(1)
                if frame.time_base < 1.0/60:
                    time_base = 1.0/60
                else:
                    time_base = frame.time_base
                frame_skip = int((time.time() - start_time)/time_base)

                print(intersection_1.intersectionMonitor(frame = image))#, intersection_2.intersectionMonitor(frame))

                if show_Video:
                    markerCorners, markerIds, rejectedCandidates = aruco.detectMarkers(image, aruco.Dictionary_get(aruco.DICT_6X6_250), parameters=aruco.DetectorParameters_create())

                    # Check if markers are detected and draw them on frame
                    if markerIds is not None:
                        image = aruco.drawDetectedMarkers(image, markerCorners, markerIds)

                    # Show video Feed
                    cv2.imshow("Camera feed", image)


            #TODO check and publish intersection status

    except (Exception, KeyboardInterrupt, SystemExit):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        drone.land()
    finally:
        drone.land()
        drone.quit()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()

