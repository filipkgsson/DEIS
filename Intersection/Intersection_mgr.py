import cv2
from cv2 import aruco
import intersection as intersection

# OpenCV Camera Feed
#cap = cv2.VideoCapture("rtsp://192.168.1.2:554/axis-media/media.amp") 
cap = cv2.VideoCapture(0)

show_Video = True

intersection_1 = intersection.Intersection([1,2,3,4])
intersection_2 = intersection.Intersection([91,92,93,94])

#### main ####
def main(args=None):
    while cv2.waitKey(1) < 0:
        try:
            hasFrame, frame = cap.read()
                    # Detect markers
            print(intersection_1.intersectionMonitor(frame = frame), intersection_2.intersectionMonitor(frame))

            if show_Video:
                markerCorners, markerIds, rejectedCandidates = aruco.detectMarkers(frame, aruco.Dictionary_get(aruco.DICT_6X6_250), parameters=aruco.DetectorParameters_create())

                # Check if markers are detected and draw them on frame
                if markerIds is not None:
                    frame = aruco.drawDetectedMarkers(frame, markerCorners, markerIds)

                # Show video Feed
                cv2.imshow("Camera feed", frame)


            #TODO check and publish intersection status

        except (Exception, KeyboardInterrupt, SystemExit):
            cv2.destroyAllWindows()
            raise

if __name__ == '__main__':
    main()

