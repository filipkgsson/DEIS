import cv2

# OpenCV Camera Feed
cap = cv2.VideoCapture("rtsp://192.168.1.2:554/axis-media/media.amp") 


def main(args=None):
    index = 0  
    while cv2.waitKey(1) < 0:
        try:
            hasFrame, frame = cap.read()
            index = index + 1

            if (index % 10) == 0:
                cv2.imwrite(('ref_images/image_%d.jpg' % (index/10)), frame)

            if index == 2000:
                break
        except (Exception, KeyboardInterrupt, SystemExit):
            cv2.destroyAllWindows()
            raise

if __name__ == '__main__':
    main()
