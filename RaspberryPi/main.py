#!/usr/bin/env python3
import serial
import time
import subprocess
import RPi.GPIO as GPIO
import threading
import signal
import os
import random
import marker_gps as gps

laneCoordinates = [530, 365, 990]
laneWidthDiff = 50
laneDiff = 90
turnDiff = 15
gpsDiff = 60
yDirection = True
negativeDirection = False
targetCoordinate = -1
targetDirection = 0
located = False
turnDirectionDiff = 70
correctionDirectionDelay = 15
correctionPositionDelay = 31
correctionDirectionDiff = 5
turnDelay = 100
currentCoordinate = -1
correctedCoordinate = -1
correctedPositionCoordinate = -1
turnCoordinate = -1
read_intersection = False
emergencyMode = False

"""
Function responsible for parsing coordinates of the robot.
"""
def gps_reader():
    while True:
        text = gps.get_gps()
        coordinates = text[0]
        direction = text[1]
        if coordinates[0] != -1:
            gps_controller(coordinates, direction)

"""
Function responsible for parsing information received from the intersection server.
The function will also send commands to the Arduino to control if the robot should drive or stop.
"""
def intersection_reader(proc):
    for line in iter(proc.stdout.readline, b''):
        text = line.strip().decode('utf-8')
        if text == '1' and not read_intersection:
            ser.write('2\n'.encode('utf-8'))
            ser.flushOutput()
            read_intersection = True
        elif text == '0' and read_intersection:
            ser.write('0\n'.encode('utf-8'))
            ser.flushOutput()
            read_intersection = False
"""
Function responsible for parsing commands given by the GPS server.
"""
def output_reader(proc):
    for line in iter(proc.stdout.readline, b''):
        text = line.strip().decode('utf-8')
        cmd = (text.split(','))[-1]
        ser.write(cmd.encode('utf-8'))

"""
Function responisble for sending commands about turning or correcting to the Arduino.
"""
def gps_controller(coordinates, direction):
    global located
    global yDirection
    global targetDirection
    global currentCoordinate
    global correctedCoordinate
    global correctedPositionCoordinate
    global turnCoordinate
    global emergencyMode

    if not located:
        located = localize(coordinates, direction)
    else:
        if yDirection:
            currentCoordinate = coordinates[1]
        else:
            currentCoordinate = coordinates[0]
        if turnCoordinate == -1 or turnCoordinate - turnDelay > currentCoordinate or currentCoordinate > turnCoordinate + turnDelay:
            if not emergencyMode and random.random() < 0.0 and turnRight(coordinates):
                ser.write('R\n'.encode('utf-8'))
                ser.flushOutput()
                targetDirection = targetDirection + 90
                if direction > 330 or direction < 50:
                    while direction < targetDirection - turnDirectionDiff or direction > 330:
                        direction = gps.get_gps()[1]
                    ser.write('F\n'.encode('utf-8'))
                    ser.flushOutput()
                else:
                    while direction < targetDirection - turnDirectionDiff:
                        direction = gps.get_gps()[1]
                    ser.write('F\n'.encode('utf-8'))
                    ser.flushOutput()

            if ((emergencyMode and targetCoordinate == laneCoordinates[2]) or (not emergencyMode and random.random() < 1.0)) and turnLeft(coordinates):
                if targetDirection == 0:
                    targetDirection = 360
                targetDirection = targetDirection - 90
                ser.write('L\n'.encode('utf-8'))
                ser.flushOutput()
                if direction > 330 or direction < 50:
                    while direction > targetDirection + turnDirectionDiff or direction < 50:
                        direction = gps.get_gps()[1]
                    ser.write('F\n'.encode('utf-8'))
                    ser.flushOutput()
                else:
                    while direction > targetDirection + turnDirectionDiff:
                        direction = gps.get_gps()[1]
                    ser.write('F\n'.encode('utf-8'))
                    ser.flushOutput()
                if yDirection:
                    turnCoordinate = coordinates[1]
                else:
                    turnCoordinate = coordinates[0]

        if correctedCoordinate == -1 or correctedCoordinate - correctionDirectionDelay > currentCoordinate or currentCoordinate > correctedCoordinate + correctionDirectionDelay:
            if correctDirectionRight(direction):
                ser.write('r\n'.encode('utf-8'))
                ser.flushOutput()
                if yDirection:
                    correctedCoordinate = coordinates[1]
                else:
                    correctedCoordinate = coordinates[0]
            elif correctDirectionLeft(direction):
                ser.write('l\n'.encode('utf-8'))
                ser.flushOutput()
                if yDirection:
                    correctedCoordinate = coordinates[1]
                else:
                    correctedCoordinate = coordinates[0]
        if correctedPositionCoordinate == -1 or correctedPositionCoordinate - correctionPositionDelay > currentCoordinate or currentCoordinate > correctedPositionCoordinate + correctionPositionDelay:
            if correctPositionRight(coordinates):
                ser.write('r\n'.encode('utf-8'))
                ser.flushOutput()
                if yDirection:
                    correctedPositionCoordinate = coordinates[1]
                else:
                    correctedPositionCoordinate = coordinates[0]
            elif correctPositionLeft(coordinates):
                ser.write('l\n'.encode('utf-8'))
                ser.flushOutput()
                if yDirection:
                    correctedPositionCoordinate = coordinates[1]
                else:
                    correctedPositionCoordinate = coordinates[0]

        if emergencyMode and 90 < coordinates[0] < 110:
            ser.write('0\n'.encode('utf-8'))
            ser.flushOutput()

"""
Function used to localize the robot when coordinates are received.
"""
def localize(coordinates, direction):
    global targetCoordinate
    global yDirection
    global negativeDirection
    global targetDirection
    global laneDiff
    localizeLaneDiff = 25

    if 80 < direction < 100:
        yDirection = False
        negativeDirection = False
        targetDirection = 90
    elif 170 < direction < 190:
        yDirection = True
        negativeDirection = False
        targetDirection = 180
    elif 260 < direction < 280:
        yDirection = False
        negativeDirection = True
        targetDirection = 270
    elif 350 < direction or direction < 10:
        yDirection = True
        negativeDirection = True
        targetDirection = 0
    else:
        return False

    if (laneCoordinates[0] - localizeLaneDiff < coordinates[1] < laneCoordinates[0] + localizeLaneDiff):
        targetCoordinate = laneCoordinates[0]
        if negativeDirection == False:
            laneDiff = 100
        return True
    elif (laneCoordinates[1] - localizeLaneDiff < coordinates[0] < laneCoordinates[1] + localizeLaneDiff):
        targetCoordinate = laneCoordinates[1]
        return True
    elif (laneCoordinates[2] - localizeLaneDiff < coordinates[0] < laneCoordinates[2] + localizeLaneDiff):
        targetCoordinate = laneCoordinates[2]
        return True
    elif (laneCoordinates[0] - laneDiff - localizeLaneDiff < coordinates[1] < laneCoordinates[0] - laneDiff + localizeLaneDiff):
        targetCoordinate = laneCoordinates[0] - laneDiff
        return True
    elif (laneCoordinates[1] - laneDiff - localizeLaneDiff < coordinates[0] < laneCoordinates[1] - laneDiff + localizeLaneDiff):
        targetCoordinate = laneCoordinates[1] - laneDiff
        return True
    elif (laneCoordinates[2] -laneDiff - localizeLaneDiff < coordinates[0] < laneCoordinates[2] - laneDiff + localizeLaneDiff):
        targetCoordinate = laneCoordinates[2] - laneDiff
        return True
    else:
        return False

"""
Function responsible for making the robot turn 90 degrees to the right.
"""
def turnRight(coordinates):
    global yDirection
    global negativeDirection
    global targetCoordinate
    global targetDirection
    global laneDiff

    if yDirection:
        if negativeDirection:
            robotCoordinate = coordinates[1] - gpsDiff
            if (laneCoordinates[0] + 10 - turnDiff/2 < robotCoordinate < laneCoordinates[0] + 10 + turnDiff/2):
                yDirection = False
                negativeDirection = False
                if targetCoordinate == laneCoordinates[1]:
                    targetCoordinate = laneCoordinates[0] + 10
                else:
                    targetCoordinate = laneCoordinates[0]
                return True
            else:
                return False
        else:
            robotCoordinate = coordinates[1] + gpsDiff
            laneDiff = 100
            if (laneCoordinates[0] - laneDiff - turnDiff/2 < robotCoordinate < laneCoordinates[0] - laneDiff + turnDiff/2):
                yDirection = False
                negativeDirection = True
                targetCoordinate = laneCoordinates[0] - laneDiff
                return True
            else:
                laneDiff = 90
                return False
    else:
        if negativeDirection:
            robotCoordinate = coordinates[0] - gpsDiff
            if (laneCoordinates[1] - turnDiff/2 < robotCoordinate < laneCoordinates[1] + turnDiff/2):
                yDirection = True
                negativeDirection = True
                targetCoordinate = laneCoordinates[1]
                return True
            elif (laneCoordinates[2] - turnDiff/2 < robotCoordinate < laneCoordinates[2] + turnDiff/2):
                yDirection = True
                negativeDirection = True
                targetCoordinate = laneCoordinates[2]
                return True
            else:
                return False
        else:
            laneDiff = 90
            turnCoordinates = [(laneCoordinates[1] - laneDiff), (laneCoordinates[2] - laneDiff + 10)]
            robotCoordinate = coordinates[0] + gpsDiff
            if (turnCoordinates[0] - turnDiff/2 < robotCoordinate < turnCoordinates[0] + turnDiff/2):
                yDirection = True
                negativeDirection = False
                targetCoordinate = laneCoordinates[1] - laneDiff
                return True
            elif (turnCoordinates[1] - turnDiff/2 < robotCoordinate < turnCoordinates[1] + turnDiff/2):
                yDirection = True
                negativeDirection = False
                targetCoordinate = laneCoordinates[2] - laneDiff
                return True
            else:
                return False

"""
Function responsible for making the robot turn 90 degrees to the left.
"""
def turnLeft(coordinates):
    global yDirection
    global negativeDirection
    global targetCoordinate
    global targetDirection
    global laneDiff

    if yDirection:
        if negativeDirection:
            robotCoordinate = coordinates[1] - gpsDiff
            laneDiff = 100
            if (laneCoordinates[0] - laneDiff - turnDiff/2 < robotCoordinate < laneCoordinates[0] - laneDiff + turnDiff/2):
                yDirection = False
                negativeDirection = True
                targetCoordinate = laneCoordinates[0] - laneDiff
                return True
            else:
                laneDiff = 90
                return False
        else:
            robotCoordinate = coordinates[1] + gpsDiff
            if (laneCoordinates[0] - turnDiff/2 < robotCoordinate < laneCoordinates[0] + turnDiff/2):
                yDirection = False
                negativeDirection = False
                targetCoordinate = laneCoordinates[0]
                return True
            else:
                return False
    else:
        if negativeDirection:
            laneDiff = 100
            robotCoordinate = coordinates[0] - gpsDiff
            if (laneCoordinates[1] - laneDiff - turnDiff/2 < robotCoordinate < laneCoordinates[1] - laneDiff + turnDiff/2):
                yDirection = True
                negativeDirection = False
                targetCoordinate = laneCoordinates[1] - laneDiff
                return True
            elif (laneCoordinates[2] - laneDiff - turnDiff/2 < robotCoordinate < laneCoordinates[2] - laneDiff + turnDiff/2):
                yDirection = True
                negativeDirection = False
                targetCoordinate = laneCoordinates[2] - laneDiff
                return True
            else:
                laneDiff = 90
                return False
        else:
            robotCoordinate = coordinates[0] + gpsDiff
            if (laneCoordinates[1] - turnDiff/2 < robotCoordinate < laneCoordinates[1] + turnDiff/2):
                yDirection = True
                negativeDirection = True
                targetCoordinate = laneCoordinates[1]
                return True
            elif (laneCoordinates[2] - turnDiff/2 < robotCoordinate < laneCoordinates[2] + turnDiff/2):
                yDirection = True
                negativeDirection = True
                targetCoordinate = laneCoordinates[2]
                return True
            else:
                return False

"""
Function used to correct the robot to the right if the direction is off.
"""
def correctDirectionRight(direction):
    if direction < targetDirection - correctionDirectionDiff:
        return True
    elif direction < 360 - correctionDirectionDiff and direction > 300:
        return True
    else:
        return False

"""
Function used to correct the robot to the right if the position is off.
"""
def correctPositionRight(coordinates):
    if yDirection:
        if negativeDirection:
            if coordinates[0] < targetCoordinate - laneWidthDiff:
                return True
            else:
                return False
        else:
            if coordinates[0] > targetCoordinate + laneWidthDiff:
                return True
            else:
                return False
    else:
        if negativeDirection:
            if coordinates[1] > targetCoordinate + laneWidthDiff:
                return True
            else:
                return False
        else:
            if coordinates[1] < targetCoordinate - laneWidthDiff:
                return True
            else:
                return False

"""
Function used to correct the robot to the left if the direction is off.
"""
def correctDirectionLeft(direction):
    if direction > targetDirection + correctionDirectionDiff:
        return True
    else:
        return False

"""
Function used to correct the robot to the left if the position is off.
"""
def correctPositionLeft(coordinates):
    if yDirection:
        if negativeDirection:
            if coordinates[0] > targetCoordinate + laneWidthDiff:
                return True
            else:
                return False
        else:
            if coordinates[0] < targetCoordinate - laneWidthDiff:
                return True
            else:
                return False
    else:
        if negativeDirection:
            if coordinates[1] < targetCoordinate - laneWidthDiff:
                return True
            else:
                return False
        else:
            if coordinates[1] > targetCoordinate + laneWidthDiff:
                return True
            else:
                return False


if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyUSB0', 115200)
    ser.flush()
    emergency_process = None
    intersection_process = None
    server_process = None
    GPIO.setwarnings(False) # Ignore warning for now
    GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
    GPIO.setup(5, GPIO.OUT, initial=GPIO.LOW) # Set pin 5 to be an output pin and set initial value to low (off)
    GPIO.setup(3, GPIO.OUT, initial=GPIO.LOW) # Set pin 3 to be an output pin and set initial value to low (off)
    intersection_process = subprocess.Popen(["ros2", "run", "intersection_sub", "IntersectionListener"], shell=False, stdout=subprocess.PIPE, cwd="/home/ubuntu/Tollgate4/intersection_ws/")
    t = threading.Thread(target=intersection_reader, args=(intersection_process,), daemon=True)
    t.start()
    gps_thread = threading.Thread(target=gps_reader, daemon=True)
    gps_thread.start()

    while True:
        text = input("Enter something: ")
        if text == "1" and emergency_process is None:
            emergency_process = subprocess.Popen(["python", "emergencyVehicle.py"], shell=False)
            gpsDiff = 130
            turnDirectionDiff = 80
            turnDelay = 200
            correctionDirectionDelay = 20
            correctionPositionDelay = 21
            correctionDirectionDiff = 2
            turnDiff = 15
            emergencyMode = True
        elif text != "1" and emergency_process is not None:
            emergency_process.terminate()
            emergency_process = None
            GPIO.output(3, GPIO.LOW)
            GPIO.output(5, GPIO.LOW)
            gpsDiff = 60
            turnDirectionDiff = 70
            turnDelay = 100
            correctionDirectionDelay = 10
            correctionPositionDelay = 31
            correctionDirectionDiff = 5
            turnDiff = 10
            emergencyMode = False
        if text == "3" and server_process is None:
            server_process = subprocess.Popen(["ros2", "run", "py_sub", "listener"], shell=False, stdout=subprocess.PIPE, cwd="/home/ubuntu/Tollgate4/gps_ws/")
            server_thread = threading.Thread(target=output_reader, args=(server_process,), daemon=True)
            server_thread.start()
        if text != "3" and server_process is not None:
            server_pid = int(subprocess.run(["pgrep", "listener"], stdout=subprocess.PIPE).stdout)
            os.kill(server_pid, signal.SIGTERM)
            server_process = None
        if text == "-1":
            ser.write("0".encode('utf-8'))
            ser.write('\n'.encode('utf-8'))
            ser.flushOutput()
            if intersection_process is not None:
                intersection_pid = int(subprocess.run(["pgrep", "IntersectionLis"], stdout=subprocess.PIPE).stdout)
                os.kill(intersection_pid, signal.SIGTERM)
                intersection_process_process = None
            ser.close()
            break
        ser.write(text.encode('utf-8'))
        ser.write('\n'.encode('utf-8'))
        ser.flushOutput()