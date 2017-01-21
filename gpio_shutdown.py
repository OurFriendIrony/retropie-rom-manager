import RPi.GPIO as GPIO
from time import sleep
from subprocess import call

#####################################################
### INITIALISATION ##################################
#####################################################

GPIO.setmode( GPIO.BOARD )
GPIO.setwarnings( False )

PIN_OFF = 32
GPIO.setup( PIN_OFF, GPIO.IN, pull_up_down=GPIO.PUD_UP )

NAP_TIME = 0.2

#####################################################
### FUNCTIONS #######################################
#####################################################

def shutdown():
    call( ["sudo", "shutdown", "now"] )

def restart():
    call( ["sudo", "shutdown", "-r", "now"] )

#####################################################
### MAIN ############################################
#####################################################

button_pressed = False
try:
    while not button_pressed:
        sleep( NAP_TIME )
        if not GPIO.input( PIN_OFF ):
            button_pressed = True
except KeyboardInterrupt:
    pass

if button_pressed:
    shutdown()

#####################################################
