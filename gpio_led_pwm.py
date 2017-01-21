import RPi.GPIO as GPIO
import time
import random

#####################################################
### INITIALISATION ##################################
#####################################################

GPIO.setmode( GPIO.BOARD )
GPIO.setwarnings( False )

PIN_RED = 40
PIN_GREEN = 38
PIN_BLUE = 36

NAP_TIME = 0.05

STEP = 5
HERTZ = 100

global initRed
global initGreen
global initBlue

lastIndex = 0
currIndex = 0

GPIO.setup( PIN_RED, GPIO.OUT )
GPIO.setup( PIN_GREEN, GPIO.OUT )
GPIO.setup( PIN_BLUE, GPIO.OUT )

initRed = GPIO.PWM( PIN_RED, HERTZ )
initGreen = GPIO.PWM( PIN_GREEN, HERTZ )
initBlue = GPIO.PWM( PIN_BLUE, HERTZ )

pwmRed = [initRed]
pwmGreen = [initGreen]
pwmBlue = [initBlue]
pwmYellow = [initRed, initGreen]
pwmCyan = [initGreen, initBlue]
pwmMagenta = [initBlue, initRed]
pwmWhite = [initRed, initGreen, initBlue]

ledIndex = [pwmRed, pwmGreen, pwmBlue, pwmYellow, pwmCyan, pwmMagenta, pwmWhite]
ledCount = len( ledIndex )

#####################################################
### FUNCTIONS #######################################
#####################################################

def nap():
    time.sleep(NAP_TIME)

def rgbPwmCycleStart(redCycle, greenCycle, blueCycle):
# Starting values for RGB
    initRed.start( redCycle )
    initGreen.start( greenCycle )
    initBlue.start( blueCycle )

def rgbPwmStop():
# Shutdown LED pwm
    initRed.stop()
    initGreen.stop()
    initBlue.stop()
    GPIO.cleanup()

def ledGlow( leds ):
# Glow the LED Set
    for intensity in range( 0, 101, STEP ):
        for led in leds:
            led.ChangeDutyCycle( intensity )
        nap()

def ledFade( leds ):
# Fade out the LED Set
    for intensity in range( 100, -1, (STEP*-1) ):
        for led in leds:
            led.ChangeDutyCycle( intensity )
        nap()

def ledGlowAndFade( colour ):
# Glow and Fade an LED Set
    ledGlow( colour )
    ledFade( colour )

def getRandomLed(): 
# Gets a random led colour - new same colour in sequence
    global lastIndex
    global currIndex

    while (currIndex == lastIndex):
        currIndex = random.randint( 0, (ledCount-1))

    lastIndex = currIndex
    return ledIndex[ currIndex ]

#####################################################
### MAIN ############################################
#####################################################

print( "CYCLE LED DEMO" )
print( "--------------" )
print( "Start" )

rgbPwmCycleStart( 0, 0, 0 )

try:
    while 1:
        ledGlowAndFade( getRandomLed() )
except KeyboardInterrupt:
	pass

rgbPwmStop()

print( "" )
print( "Finish" )

#####################################################
