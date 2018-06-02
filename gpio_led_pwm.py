import RPi.GPIO as GPIO
import time
import random

#####################################################

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

PIN_RED = 40
PIN_GREEN = 38
PIN_BLUE = 36

NAP_TIME = 0.05

STEP = 5
HERTZ = 100

global initRed
global initGreen
global initBlue

last_index = 0
curr_index = 0

GPIO.setup(PIN_RED, GPIO.OUT)
GPIO.setup(PIN_GREEN, GPIO.OUT)
GPIO.setup(PIN_BLUE, GPIO.OUT)

initRed = GPIO.PWM(PIN_RED, HERTZ)
initGreen = GPIO.PWM(PIN_GREEN, HERTZ)
initBlue = GPIO.PWM(PIN_BLUE, HERTZ)

pwmRed = [initRed]
pwmGreen = [initGreen]
pwmBlue = [initBlue]
pwmYellow = [initRed, initGreen]
pwmCyan = [initGreen, initBlue]
pwmMagenta = [initBlue, initRed]
pwmWhite = [initRed, initGreen, initBlue]

ledIndex = [pwmRed, pwmGreen, pwmBlue, pwmYellow, pwmCyan, pwmMagenta, pwmWhite]
ledCount = len(ledIndex)


#####################################################

def nap():
    time.sleep(NAP_TIME)


def rgb_pwm_cycle_start(red_cycle, green_cycle, blue_cycle):
    # Starting values for RGB
    initRed.start(red_cycle)
    initGreen.start(green_cycle)
    initBlue.start(blue_cycle)


def rgb_pwm_stop():
    # Shutdown LED pwm
    initRed.stop()
    initGreen.stop()
    initBlue.stop()
    GPIO.cleanup()


def led_glow(leds):
    # Glow the LED Set
    for intensity in range(0, 101, STEP):
        for led in leds:
            led.ChangeDutyCycle(intensity)
        nap()


def led_fade(leds):
    # Fade out the LED Set
    for intensity in range(100, -1, (STEP * -1)):
        for led in leds:
            led.ChangeDutyCycle(intensity)
        nap()


def led_glow_and_fade(colour):
    # Glow and Fade an LED Set
    led_glow(colour)
    led_fade(colour)


def get_random_led():
    # Gets a random led colour - new same colour in sequence
    global last_index
    global curr_index

    while curr_index == last_index:
        curr_index = random.randint(0, (ledCount - 1))

        last_index = curr_index
    return ledIndex[curr_index]


#####################################################

print("CYCLE LED DEMO")
print("--------------")
print("Start")

rgb_pwm_cycle_start(0, 0, 0)

try:
    while True:
        led_glow_and_fade(get_random_led())
except KeyboardInterrupt:
    pass

rgb_pwm_stop()

print("")
print("Finish")

#####################################################
