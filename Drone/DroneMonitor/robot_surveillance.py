import sys
import traceback
import tellopy
import av
import cv2
from cv2 import aruco
import numpy as np
import time
import intersection as intersection
from simple_pid import PID

# ArUco dictionary and default detector parameters
dictionary = aruco.Dictionary_get(aruco.DICT_6X6_250)
parameters = aruco.DetectorParameters_create()

x_center = 960/2
y_center = 720/2
th = 10
limit = 20

pidX = PID(10, 0.2, 0.0002, setpoint=x_center, sample_time=0.1, output_limits=(-limit,limit))
pidY = PID(10, 0.2, 0.0002, setpoint=y_center, sample_time=0.1, output_limits=(-limit,limit))

# Intersection marker id's
m1 = 1
m2 = 2
m3 = 3
m4 = 4
m5 = 91
m6 = 92
m7 = 93
m8 = 94

mR = 42         # robot ID

ids = np.array([m1,m2,m3,m4,m5,m6,m7,m8])

def centeroidnp(arr):
    length = arr.shape[0]
    sum_x = np.sum(arr[:, 0])
    sum_y = np.sum(arr[:, 1])
    
    return sum_x/length, sum_y/length
    
def get_cornerPoint(ids, id, corners, corner):
    index = np.squeeze(np.where(ids==id))
    point = np.squeeze(corners[index[0]])[corner]

    return point
    
def main():
    drone = tellopy.Tello()

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
        time.sleep(5)       # time for drone self-calibration
        drone.up(20) 
        time.sleep(0.1)
        
        while True:

            drone.up(0)
            for frame in container.decode(video=0):
                if 0 < frame_skip:
                    frame_skip = frame_skip - 1
                    continue


                start_time = time.time()

                image = cv2.cvtColor(np.array(frame.to_image()), cv2.COLOR_RGB2BGR)

                markerCorners, markerIds, rejectedCandidates = aruco.detectMarkers(image, dictionary, parameters=parameters)
                
                if markerIds is not None:       # 1+ marker(s) detected
                    inters_mark = 0
                    for x in markerIds:
                        if x in ids:
                            inters_mark += 1    # count number of detected intersection markers
                    
                    if True:     # default mode: following robot
                        drone.up(0)             # prevent uncontrolled increase of altitude 
                                    
                        if mR in markerIds:   # just follow robot
                            indR = np.squeeze(np.where(markerIds==mR))[0]
                            center = centeroidnp(markerCorners[indR][0])

                            if center[0] < (x_center - th):
                                print("left")
                                drone.left(10)

                            elif center[0] > (x_center + th):
                                print("right")
                                drone.right(10)

                            if center[1] < (y_center - th):
                                print("forward")
                                drone.forward(10)

                            elif center[1] > (y_center + th):
                                print("backward")
                                drone.backward(10)

                            print(centeroidnp(markerCorners[indR][0]), image.shape, inters_pos)     # control information
                        
                cv2.imshow('Original', image)

                cv2.waitKey(1)
                if frame.time_base < 1.0/60:
                    time_base = 1.0/60
                else:
                    time_base = frame.time_base
                frame_skip = int((time.time() - start_time)/time_base)
                    

    except Exception as ex:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        print(ex)
    finally:
        drone.land()
        drone.quit()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()