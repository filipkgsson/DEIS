# imports (...)

# (...)

# setup PID controller
pidX = PID(10, 0.2, 0.0002, setpoint=x_center, sample_time=0.1, output_limits=(-limit,limit))
pidY = PID(10, 0.2, 0.0002, setpoint=y_center, sample_time=0.1, output_limits=(-limit,limit))

# Intersection marker id's
# (...)

ids = np.array([m1,m2,m3,m4,m5,m6,m7,m8])

inters_pos = 0
inters_mark = 0

#   (...)
    
def main():
    drone = tellopy.Tello()

#   (...)
        
    # skip first 300 frames
    frame_skip = 300
    drone.takeoff()
    time.sleep(5)       # calibration time for drone
    
    # just to get sure
    inters_pos = 0
    inters_mark = 0
    
    drone.up(20) 
    time.sleep(0.1)
    
    while True:

        drone.up(0)     # prevent uncontrolled increase of altitude 
        for frame in container.decode(video=0):
            if 0 < frame_skip:
                frame_skip = frame_skip - 1
                continue

            start_time = time.time()

            image = cv2.cvtColor(np.array(frame.to_image()), cv2.COLOR_RGB2BGR)

            markerCorners, markerIds, rejectedCandidates = aruco.detectMarkers(image, dictionary, parameters=parameters)
            
            if markerIds is not None:       # 1+ marker detected
                inters_mark = 0
                for x in markerIds:
                    if x in ids:
                        inters_mark += 1
                
                if inters_pos == 0:         # standby / following robot / entering intersection
                    if inters_mark == 4:    # fully over intersection
                        inters_pos = 1
                            # send stop signal to robot (...)
                            
                    elif mR in markerIds:   # start from robot
                        drone.forward(10)
                        time.sleep(0.1)
                        drone.left(10)      # out-balance drift

                    else:
                        drone.forward(10)
                        time.sleep(0.1)
                        drone.up(10)        # increase altitude to get better overview

                elif inters_pos == 1:    # check intersection

                    if mR in markerIds:     # robot continued driving
                            inters_pos = 2  
                    
                    else:
                        # hold position above intersection
                        # Get inside corners of ROI marked by ArUco markers
                        roi_corners = np.array([
                            get_cornerPoint(markerIds, ids[0], markerCorners, 0), get_cornerPoint(markerIds, ids[1], markerCorners, 0),
                            get_cornerPoint(markerIds, ids[2], markerCorners, 0), get_cornerPoint(markerIds, ids[3], markerCorners, 0)
                         ])
                        center = centeroidnp(roi_corners)
                        x = pidX(center[0])                                
                        if x > 0:
                            drone.left(x)                                
                        else:
                            drone.right(-x)

                        y = pidY(center[1])                                
                        if y > 0:
                            drone.forward(y)                                
                        else:
                            drone.backward(-y)
                        print(centeroidnp(roi_corners), image.shape)
                        # check intersection (see intersection.py/Appendix C)
                        # send start signal to robot when free (...)

                elif inters_pos == 2:   # leave intersection
                
                    if inters_mark > 0: # still above intersection
                    
                        if mR in markerIds:     # center on robot again
                            indR = np.squeeze(np.where(markerIds==mR))
                            center = centeroidnp(markerCorners[indR][indR])
                            x = pidX(center[0])                                
                            if x > 0:
                                drone.left(x)                                
                            else:
                                drone.right(-x)

                            y = pidY(center[1])                                
                            if y > 0:
                                drone.forward(y)                                
                            else:
                                drone.backward(-y)

                        else:   # "Error case": intersection not fully left, but robot lost
                            drone.forward(0)
                            drone.backward(0)
                            drone.left(0)
                            drone.right(0)
                    else:   # left intersection, return to initial mode
                        inters_pos = 0
                        
            else:       # search for marker
                drone.forward(10)
                time.sleep(0.1)
                drone.left(10)      # out-balance drift
                    
#   (...)