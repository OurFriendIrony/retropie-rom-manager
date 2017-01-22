import os, logging, random, time
from shutil import move
from datetime import datetime
from pygame import mixer # import PyGame's music mixer

#####################################################
### CONFIG ##########################################
#####################################################

# MUSIC CONFIG
VOLUME_MIN = 0.0
VOLUME_MAX = 0.4
VOLUME_FADE_RATE = 0.05
VOLUME_FADE_DELAY = 0.2

MUSIC_DIR = "/home/pi/BGM"
MUSIC_LIST = [mp3 for mp3 in os.listdir(MUSIC_DIR) if mp3[-4:] == ".mp3" or mp3[-4:] == ".ogg"]
MUSIC_LIST_NUM = len( MUSIC_LIST )
MUSIC_RESTART = False                   # False = Music resumes | True = Music restarts
MUSIC_ONLY_THIS = ""                    # Force only this song to play

# PROCESS LISTS
PROCESS_EMUSTAT = "emulationstatio"
PROCESS_VIDEO = ["omxplayer","omxplayer.bin"]
PROCESS_EMULATORS = ["retroarch","advmame","ags","alephone","atari800","basiliskll","cannonball","capricerpi","cgenesis","daphne","dgen","dosbox","eduke32","fbzx","frotz","fuse","gemrb","gngeo","gpsp","hatari","ioquake3","jzintv","kodi","linapple","lincity","love","mame","micropolis","mupen64plus","openbor","openmsx","openttd","opentyrian","osmose","pifba","pisnes","ppsspp","reicast","residualvm","scummvm","sdlpop","simcoupe","snes9x","solarus","stella","stratagus","tyrquake","uae4all2","uae4arm","uqm","vice","wolf4sdl","xrick","xroar","zdoom"]

# LOGGING SETUP
SCRIPT_NAME = os.path.basename(__file__)
LOG_NAME = SCRIPT_NAME[:-3] + ".log"
LOG_DIR = os.path.dirname(os.path.abspath(__file__)) + "/logs/"
LOG_FILE = LOG_DIR + LOG_NAME
if not os.path.exists(os.path.dirname(LOG_DIR)):
    os.makedirs(os.path.dirname(LOG_DIR))
if os.path.isfile(LOG_FILE):
    move(LOG_FILE, LOG_FILE+".bak")
logging.basicConfig( filename=LOG_FILE, level=logging.INFO )

# VARS & OBJECTS
lastsong = -1
currentSongIndex = -1
mixer.init()
random.seed()

# Debug
LOG_LEVEL = "INFO"

#####################################################
### FUNCTIONS #######################################
#####################################################

def logLevel( level ):
    if level == "OFF":      # Nothing
        return 0
    elif level == "ERROR":  # Only worst
        return 1
    elif level == "INFO":   # Normal
        return 2
    else:                   # Every tiny detail
        return 3

def log( message ):
    now = datetime.now().strftime("[%Y-%m-%d] [%H:%M:%S]")
    logging.info( now +" "+ message )

def log2( levelString, message ):
    if logLevel( levelString ) <= logLevel( LOG_LEVEL ):
        now = datetime.now().strftime("[%Y-%m-%d] [%H:%M:%S]")
        level = "["+levelString.ljust(5)+"]"
        logging.info( now +" "+level+" "+ message )
    
def adjustVolume( newVolume ):
    global mixer
    mixer.music.set_volume( newVolume )
    
def startSong(forceStart):
    global MUSIC_RESTART, mixer
    if MUSIC_RESTART or forceStart:
        mixer.music.rewind()
        mixer.music.play()
        log2("INFO","Audio started")
    else:
        mixer.music.unpause()
        log2("INFO","Audio resumed")
        
def stopSong():
    global MUSIC_RESTART, mixer
    if MUSIC_RESTART:
        mixer.music.stop() 
        log2("INFO","Audio stopped")
    else:
        mixer.music.pause() 
        log2("INFO","Audio paused")

def fadeVolumeUp(forceStart):
    global VOLUME_FADE_RATE, VOLUME_MAX, VOLUME_MIN
    currVolume = VOLUME_MIN
    adjustVolume( currVolume )
    startSong(forceStart)
    log2("DEBUG","VolumeUp from "+str(currVolume)+" to "+str(VOLUME_MAX))
    while not ( currVolume >= VOLUME_MAX ):
        currVolume += VOLUME_FADE_RATE
        adjustVolume( currVolume )
        time.sleep( VOLUME_FADE_DELAY )
    adjustVolume( VOLUME_MAX )

def fadeVolumeDown():
    global VOLUME_FADE_RATE, VOLUME_MAX, VOLUME_MIN
    currVolume = VOLUME_MAX
    adjustVolume( currVolume )
    log2("DEBUG","VolumeDown from "+str(currVolume)+" to "+str(VOLUME_MIN))
    while not ( currVolume <= VOLUME_MIN ):
        currVolume -= VOLUME_FADE_RATE
        adjustVolume( currVolume )
        time.sleep( VOLUME_FADE_DELAY )
    adjustVolume( VOLUME_MIN )
    stopSong()

def getProcessIds():
    return [pid for pid in os.listdir('/proc') if pid.isdigit()]

def getProcessName(pid):
    return open(os.path.join('/proc',pid,'comm'),'rb').read()[:-1] # Remove last character (new line)

#####################################################
### INIT ############################################
#####################################################

log2("INFO","Log : "+LOG_FILE)

# Ensure we have music to play 
if MUSIC_LIST_NUM == 0:
    log2("ERROR","No music to play...")
    sys.exit()
elif MUSIC_LIST_NUM == 1:           # If only one song exists, force it
    MUSIC_ONLY_THIS = MUSIC_LIST[0]
    log2("DEBUG","Single song selected ["+MUSIC_ONLY_THIS+"]")

# Wait for EmulationStation to start
log2("INFO","Waiting for EmulationStation to start...")
esIsRunning = False
while not esIsRunning:
    time.sleep(1)
    pids = getProcessIds()
    for pid in pids:
        try:
            procname = getProcessName(pid)
            if procname == PROCESS_EMUSTAT:
                esIsRunning = True
        except IOError: 
            continue
    
# Wait for OMXPlayer to finish (video splashscreen player)
log2("INFO","Checking for splashscreen video [OMXplayer]")
pids = getProcessIds()
for pid in pids:
    try:
        procname = getProcessName(pid)
        if procname in PROCESS_VIDEO:
            log2("INFO","Waiting for splashscreen video to end... ["+procname+"]")
            while os.path.exists('/proc/'+pid):
                time.sleep(1)
    except IOError: 
        continue

#####################################################
### MAIN ############################################
#####################################################

log2("INFO","Starting main sequence...")
while True:
    time.sleep(1);

    # Check to see if EmulationStation has closed (for instance, dropping to terminal)
    if not esIsRunning:
        log2("INFO","EmulationStation stopped running")
        while not esIsRunning:
            log2("DEBUG","Waiting for EmulationStation to restart... [In Terminal?]")
            if mixer.music.get_volume() > 0:
                fadeVolumeDown()
            time.sleep(1)
            
            pids = getProcessIds()
            for pid in pids:
                try:
                    procname = getProcessName(pid)
                    if procname == PROCESS_EMUSTAT:
                        esIsRunning = True
                        fadeVolumeUp(forceStart=False)
                        log2("INFO","EmulationStation started running")
                        break

                except IOError: 
                    continue
    log2("DEBUG","EmulationStation running...")

    # Pick track to start playing music
    if not mixer.music.get_busy():
        log2("INFO","Loading new music")
        if not MUSIC_ONLY_THIS == "":
            currentSongIndex = MUSIC_LIST.index( MUSIC_ONLY_THIS )
        else:
            while currentSongIndex == lastsong:
                currentSongIndex = random.randint( 0, MUSIC_LIST_NUM - 1 )
        song = os.path.join(MUSIC_DIR, MUSIC_LIST[currentSongIndex])
        mixer.music.load(song) 
        log2("INFO","Loaded music [" + song+"]")
        lastsong=currentSongIndex
        fadeVolumeUp(forceStart=True)
    log2("DEBUG","Music playing...")
        
    # Emulator check
    pids = getProcessIds()
    esIsRunning = False
    for pid in pids:
        try:
            procname = getProcessName(pid)
            # Is EmulationStation running
            if procname == PROCESS_EMUSTAT:
                log2("DEBUG","EmulationStation is still running...")
                esIsRunning = True

            # Is one of the known emulators running
            if procname in PROCESS_EMULATORS:
                log2("INFO","Emulator started ["+procname+"]")
                fadeVolumeDown()

                log2("INFO","Waiting for emulator to finish... ["+procname+"]")
                while os.path.exists("/proc/" + pid):
                    time.sleep(1)

                fadeVolumeUp(forceStart=False)
                log2("INFO","Emulator finished ["+procname+"]")
        except IOError:
            continue
    log2("DEBUG","No emulator running...")
    
#####################################################

log2("ERROR","An error has occurred that has stopped "+SCRIPT_NAME+" from executing.")

#####################################################

