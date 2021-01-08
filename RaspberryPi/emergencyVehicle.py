import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import time # Import the sleep function from the time module
import sys
import atexit

def emergency():
    atexit.register(onExit)
    GPIO.setwarnings(False) # Ignore warning for now
    GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
    GPIO.setup(5, GPIO.OUT, initial=GPIO.LOW) # Set pin 8 to be an output pin and set initial value to low (off)
    GPIO.setup(3, GPIO.OUT, initial=GPIO.LOW) # Set pin 8 to be an output pin and set initial value to low (off)

    i = 0
    while True: # Run forever
        GPIO.output(5, GPIO.HIGH) # Turn on
        GPIO.output(3, GPIO.HIGH) # Turn on
        time.sleep(0.001) # Sleep for 1 second
        GPIO.output(5, GPIO.LOW) # Turn off
        GPIO.output(3, GPIO.LOW) # Turn off
        time.sleep(0.001) # Sleep for 1 second
        if(i >= 250):
            time.sleep(0.05)
            i = 0
        i += 1

def onExit():
    GPIO.output(5, GPIO.LOW)
    GPIO.output(3, GPIO.LOW)

if __name__ == "__main__":
    emergency()
    """if(sys.argv[1] == "1"):
        emergency()
    else:
        cancel()"""
