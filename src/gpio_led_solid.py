#!/usr/bin/python

import RPi.GPIO as GPIO
import time

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

def pin_change(pin, status):
    if status:
        GPIO.output(pin, GPIO.HIGH)
    else:
        GPIO.output(pin, GPIO.LOW)


def rgb(status_red, status_green, status_blue):
    pin_change(PIN_RED, status_red)
    pin_change(PIN_GREEN, status_green)
    pin_change(PIN_BLUE, status_blue)


def nap():
    time.sleep(NAP_TIME)


def rgb_plus_nap(status_red, status_green, status_blue):
    nap()
    rgb(status_red, status_green, status_blue)


#####################################################

print("SOLID LED DEMO")
print("--------------")
print("Start")

try:
    while True:
        rgb_plus_nap(ON, OFF, OFF)
        rgb_plus_nap(OFF, ON, OFF)
        rgb_plus_nap(OFF, OFF, ON)
        rgb_plus_nap(ON, ON, OFF)
        rgb_plus_nap(OFF, ON, ON)
        rgb_plus_nap(ON, OFF, ON)
        rgb_plus_nap(ON, ON, ON)
except KeyboardInterrupt:
    pass

rgb(OFF, OFF, OFF)

print("Finish")

#####################################################
