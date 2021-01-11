import cv2
from cv2 import aruco
import numpy as np

# OpenCV Camera Feed
cap = cv2.VideoCapture("rtsp://192.168.1.2:554/axis-media/media.amp") 
#cap = cv2.VideoCapture(0)

show_Video = True

ids = [91,92,93,94]
roi_size = 100
roi_shape = np.array([[0.0,0.0],[roi_size, 0.0],[ 0.0,roi_size],[roi_size, roi_size]])

band_size = 100


def get_cornerPoint( ids, id, corners):
    index = np.squeeze(np.where(ids == id))
    point = np.squeeze(corners[index[0]])[0]
    return point


#### main ####
def main(args=None):
    while cv2.waitKey(1) < 0:
        try:
            hasFrame, frame = cap.read()

            if show_Video:
                markerCorners, markerIds, rejectedCandidates = aruco.detectMarkers(frame, aruco.Dictionary_get(aruco.DICT_6X6_250), parameters=aruco.DetectorParameters_create())

                # Check if markers are detected and draw them on frame
                # if markerIds is not None:
                #     frame2 = aruco.drawDetectedMarkers(frame, markerCorners, markerIds)

                # Show video Feed
                #cv2.imshow("Camera feed", frame)

                if markerIds is None:
                    print('Markers not detected')
                    return -1

                
                # Check that all corners are present

                if all(x in markerIds for x in ids):

                    roi_corners = np.array([
                        get_cornerPoint(markerIds, ids[0], markerCorners), get_cornerPoint(markerIds, ids[1], markerCorners),
                        get_cornerPoint(markerIds, ids[2], markerCorners), get_cornerPoint(markerIds, ids[3], markerCorners)
                    ])


                            # Prepare a mask representing region to copy from the warped image into the original frame.
                    # mask = np.zeros([frame.shape[0], frame.shape[1]], dtype=np.uint8);
                    # cv2.fillConvexPoly(mask, np.int32([roi_corners]), ((255, 255, 255)), cv2.LINE_AA);
                    # cv2.imshow("Mask", mask)


                    # Start coordinate, here (5, 5) 
                    # represents the top left corner of rectangle 
                    start_point = (5, 5) 
                    
                    # Ending coordinate, here (220, 220) 
                    # represents the bottom right corner of rectangle 
                    end_point = (220, 220) 
                    
                    # Blue color in BGR 
                    color = (0, 0, 0) 
                    
                    # Line thickness of 2 px 
                    thickness = -1
                    
                    # Using cv2.rectangle() method 
                    # Draw a rectangle with blue line borders of thickness of 2 px 
                    frame = cv2.rectangle(frame, tuple(roi_corners[0]), tuple(roi_corners[3]), color, thickness) 
                    cv2.imshow("Camera feed", frame)
                    
                    # # Erode the mask to not copy the boundary effects from the warping
                    # element = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3));
                    # mask = cv2.erode(mask, element, iterations=3);

                    # # Copy the mask into 3 channels.
                    # warped_image = np.zeros([frame.shape[0], frame.shape[1],3], dtype=np.uint8);
                    # mask3 = np.zeros_like(warped_image)
                    # for i in range(0, 3):
                    #     mask3[:,:,i] = mask/255

                    # # Copy the warped image into the original frame in the mask region.
                    # warped_image_masked = cv2.multiply(warped_image, mask3)
                    # frame_masked = cv2.multiply(frame.astype(float), 1-mask3)

                    # im_out = cv2.add(frame, mask)
                    # cv2.imshow("Region of interest masqk", im_out)


                    # print(roi_corners)
                    roi_corners[0] = [roi_corners[0][0] - band_size, roi_corners[0][1] - band_size]
                    roi_corners[1] = [roi_corners[1][0] + band_size, roi_corners[1][1] - band_size]
                    roi_corners[2] = [roi_corners[2][0] - band_size, roi_corners[2][1] + band_size]
                    roi_corners[3] = [roi_corners[3][0] + band_size, roi_corners[3][1] + band_size]

                    # Get homography and warp image feed into roi
                    h, status = cv2.findHomography(roi_corners, roi_shape)
                    roi = cv2.warpPerspective(frame, h, (roi_size,roi_size))
                    

                    
                    cv2.imshow("Region of interest raw", roi)

                    markerCorners, markerIds, rejectedCandidates = aruco.detectMarkers(roi, aruco.Dictionary_get(aruco.DICT_6X6_250), parameters=aruco.DetectorParameters_create())
                    print(markerIds)



            #TODO check and publish intersection status

        except (Exception, KeyboardInterrupt, SystemExit):
            cv2.destroyAllWindows()
            raise

if __name__ == '__main__':
    main()

