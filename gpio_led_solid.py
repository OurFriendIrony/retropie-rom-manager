import RPi.GPIO as GPIO
import time

#####################################################
### INITIALISATION ##################################
#####################################################

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

PIN_RED = 40
PIN_GREEN = 38
PIN_BLUE = 36

ON = 1
OFF = 0

NAP_TIME = 0.5

GPIO.setup(PIN_RED, GPIO.OUT)
GPIO.setup(PIN_GREEN, GPIO.OUT)
GPIO.setup(PIN_BLUE, GPIO.OUT)

#####################################################
### FUNCTIONS #######################################
#####################################################

def pinChange(pin, status):
    if status:
        GPIO.output(pin, GPIO.HIGH)
    else:
        GPIO.output(pin, GPIO.LOW)

def rgb(redStatus, greenStatus, blueStatus):
    pinChange(PIN_RED, redStatus)
    pinChange(PIN_GREEN, greenStatus)
    pinChange(PIN_BLUE, blueStatus)

def nap():
    time.sleep(NAP_TIME)

def rgbPlusNap(redStatus, greenStatus, blueStatus):
    nap()
    rgb(redStatus, greenStatus, blueStatus)

#####################################################
### MAIN ############################################
#####################################################

print( "SOLID LED DEMO" )
print( "--------------" )
print( "Start" )

try:
    while 1:
        rgbPlusNap(ON, OFF, OFF)
        rgbPlusNap(OFF, ON, OFF)
        rgbPlusNap(OFF, OFF, ON)
        rgbPlusNap(ON, ON, OFF)
        rgbPlusNap(OFF, ON, ON)
        rgbPlusNap(ON, OFF, ON)
        rgbPlusNap(ON, ON, ON)
except KeyboardInterrupt:
    pass

rgb(OFF, OFF, OFF)

print( "Finish" )

#####################################################
