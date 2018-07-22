#!/usr/bin/python

import logging
import os
import random
import sys
import time
from shutil import move

import RPi.GPIO as GPIO
from pygame import mixer  # "sudo apt-get install python-pygame"

#####################################################

# LOGGING SETUP
SCRIPT_NAME = os.path.basename(__file__)
LOG_NAME = SCRIPT_NAME[:-3] + ".log"
LOG_DIR = os.path.dirname(os.path.abspath(__file__)) + "/logs/"
LOG_FILE = LOG_DIR + LOG_NAME
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(message)s"
if not os.path.exists(os.path.dirname(LOG_DIR)):
    os.makedirs(os.path.dirname(LOG_DIR))
if os.path.isfile(LOG_FILE):
    move(LOG_FILE, LOG_FILE + ".bak")

logging.basicConfig(filename=LOG_FILE, format=LOG_FORMAT, level=logging.INFO)
logger = logging.getLogger("bgm")

# MUSIC CONFIG
VOLUME_MIN = 0.0
VOLUME_MAX = 0.4
VOLUME_FADE_RATE = 0.05
VOLUME_FADE_DELAY = 0.3

MUSIC_DIR = "/home/pi/RetroPie/bgm"
MUSIC_PLAY_ONLY = ""  # Force only this song to play
try:
    MUSIC_LIST = [mp3 for mp3 in os.listdir(MUSIC_DIR) if mp3[-4:] == ".mp3"]
except Exception:
    MUSIC_LIST = ""
MUSIC_RESTART = False  # False = Music resumes | True = Music restarts

# If only one song exists, force it
if not MUSIC_PLAY_ONLY == "":
    if MUSIC_PLAY_ONLY in MUSIC_LIST:
        MUSIC_LIST = [MUSIC_PLAY_ONLY]
        logger.debug("Single song selected [" + MUSIC_PLAY_ONLY + "]")

# PROCESS LISTS
PROCESS_EMUSTAT = "emulationstatio"
PROCESS_VIDEO = ["omxplayer", "omxplayer.bin"]
PROCESS_EMULATORS = ["retroarch", "advmame", "ags", "alephone", "atari800", "basiliskll", "bgdi-330", "cannonball",
                     "capricerpi", "cgenesis", "daphne", "dgen", "dosbox", "eduke32", "fbzx", "frotz", "fuse", "gemrb",
                     "gngeo", "gpsp", "hatari", "ioquake3", "ioquake3.arm", "jzintv", "kodi", "linapple", "lincity",
                     "love", "mame", "micropolis", "mupen64plus", "openbor", "openmsx", "openttd", "opentyrian",
                     "osmose", "pifba", "pisnes", "ppsspp", "reicast", "residualvm", "scummvm", "sdlpop", "simcoupe",
                     "snes9x", "solarus", "stella", "stratagus", "tyrquake", "uae4all2", "uae4arm", "uqm", "vice",
                     "wolf4sdl", "wolf4sdl-sw-v14", "xrick", "xroar", "zdoom"]

# GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
PIN_BUTTON = 32
GPIO.setup(PIN_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# VARS & OBJECTS
playedSongs = []

mixer.init()
random.seed()


#####################################################

def adjust_volume(new_volume):
    mixer.music.set_volume(new_volume)


def start_song(force_restart):
    if MUSIC_RESTART or force_restart:
        mixer.music.rewind()
        mixer.music.play()
        logger.info("Audio started")
    else:
        mixer.music.unpause()
        logger.info("Audio resumed")


def stop_song():
    if MUSIC_RESTART:
        mixer.music.stop()
        logger.info("Audio stopped")
    else:
        mixer.music.pause()
        logger.info("Audio paused")


def fade_volume_up(force_restart):
    curr_volume = VOLUME_MIN
    adjust_volume(curr_volume)
    start_song(force_restart)
    logger.debug("VolumeUp from " + str(curr_volume) + " to " + str(VOLUME_MAX))
    while not (curr_volume >= VOLUME_MAX):
        curr_volume += VOLUME_FADE_RATE
        adjust_volume(curr_volume)
        time.sleep(VOLUME_FADE_DELAY)
    adjust_volume(VOLUME_MAX)


def fade_volume_down():
    curr_volume = VOLUME_MAX
    adjust_volume(curr_volume)
    logger.debug("VolumeDown from " + str(curr_volume) + " to " + str(VOLUME_MIN))
    while not (curr_volume <= VOLUME_MIN):
        curr_volume -= VOLUME_FADE_RATE
        adjust_volume(curr_volume)
        time.sleep(VOLUME_FADE_DELAY)
    adjust_volume(VOLUME_MIN)
    stop_song()


def get_process_ids():
    return [pid for pid in os.listdir('/proc') if pid.isdigit()]


def get_process_name(pid):
    return open(os.path.join('/proc', pid, 'comm'), 'rb').read()[:-1]  # Remove last character (new line)


def button_was_pressed():
    try:
        if not GPIO.input(PIN_BUTTON):
            logger.info("Button was pressed [" + str(PIN_BUTTON) + "]")
            return True
    except KeyboardInterrupt:
        pass
    return False


def track_played_songs(index):
    global playedSongs
    playedSongs.append(index)
    if len(playedSongs) == len(MUSIC_LIST):
        playedSongs = [index]
    logger.debug("Tracked Songs: " + str(playedSongs))


#####################################################

logger.info("Log : " + LOG_FILE)

# Ensure we have music to play
if len(MUSIC_LIST) == 0:
    logger.warning("No music to play...")
    sys.exit()

# Wait for EmulationStation to start
logger.info("Waiting for EmulationStation to start...")
esIsRunning = False
while not esIsRunning:
    time.sleep(1)
    pids = get_process_ids()
    for pid in pids:
        try:
            procname = get_process_name(pid)
            if procname == PROCESS_EMUSTAT:
                esIsRunning = True
        except IOError:
            logger.error("Failed to read process record")
            continue

# Wait for OMXPlayer to finish (video splashscreen player)
logger.info("Checking for splashscreen video [OMXplayer]")
pids = get_process_ids()
for pid in pids:
    try:
        procname = get_process_name(pid)
        if procname in PROCESS_VIDEO:
            logger.info("Waiting for splashscreen video to end... [" + procname + "]")
            while os.path.exists('/proc/' + pid):
                time.sleep(1)
    except IOError:
        continue

#####################################################

logger.info("Starting main sequence...")
while True:
    time.sleep(1);

    # Check to see if EmulationStation has closed (for instance, dropping to terminal)
    if not esIsRunning:
        logger.info("EmulationStation stopped running")
        while not esIsRunning:
            logger.debug("Waiting for EmulationStation to restart... [In Terminal?]")
            if mixer.music.get_volume() > 0:
                fade_volume_down()
            time.sleep(1)

            pids = get_process_ids()
            for pid in pids:
                try:
                    procname = get_process_name(pid)
                    if procname == PROCESS_EMUSTAT:
                        esIsRunning = True
                        fade_volume_up(force_restart=False)
                        logger.info("EmulationStation started running")
                        break

                except IOError:
                    continue
    logger.debug("EmulationStation running...")

    # Pick track to start playing music
    buttonPressed = button_was_pressed()
    if not mixer.music.get_busy() or buttonPressed:
        if buttonPressed:
            fade_volume_down()
        logger.info("Loading new music")
        currentSongIndex = random.randint(0, len(MUSIC_LIST) - 1)
        while currentSongIndex in playedSongs:
            currentSongIndex = random.randint(0, len(MUSIC_LIST) - 1)
        track_played_songs(currentSongIndex)
        song = os.path.join(MUSIC_DIR, MUSIC_LIST[currentSongIndex])
        mixer.music.load(song)
        logger.info("Loaded music [" + song + "]")
        fade_volume_up(force_restart=True)
    logger.debug("Music playing...")

    # Emulator check
    pids = get_process_ids()
    esIsRunning = False
    for pid in pids:
        try:
            procname = get_process_name(pid)
            # Is EmulationStation running
            if procname == PROCESS_EMUSTAT:
                logger.debug("EmulationStation is still running...")
                esIsRunning = True

            # Is one of the known emulators running
            if procname in PROCESS_EMULATORS:
                logger.info("Emulator started [" + procname + "]")
                fade_volume_down()

                logger.info("Waiting for emulator to finish... [" + procname + "]")
                while os.path.exists("/proc/" + pid):
                    time.sleep(1)

                fade_volume_up(force_restart=False)
                logger.info("Emulator finished [" + procname + "]")
        except IOError:
            continue
    logger.debug("No emulator running...")

#####################################################
