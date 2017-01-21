import os, logging, random, time
from shutil import move
from datetime import datetime
from pygame import mixer # import PyGame's music mixer

# MUSIC CONFIG
VOLUME_MIN = 0.0
VOLUME_MAX = 0.4
VOLUME_FADE_RATE = 0.05
VOLUME_FADE_DELAY = 0.2

MUSIC_DIR = "/home/pi/BGM"
MUSIC_LIST = [mp3 for mp3 in os.listdir(MUSIC_DIR) if mp3[-4:] == ".mp3" or mp3[-4:] == ".ogg"] # Find everything that's .mp3 or .ogg

startdelay = 0 # Value (in seconds) to delay audio start.  If you have a splash screen with audio and the script is playing music over the top of it, increase this value to delay the script from starting.
RESTART_MODE = True # If true, this will cause the script to fade the music out and -stop- the song rather than pause it.
startsong = "" # if this is not blank, this is the EXACT, CaSeSeNsAtIvE filename of the song you always want to play first on boot.

lastsong = -1
currentSongIndex = -1
mixer.init() # Prep that bad boy up.
random.seed()
volume = VOLUME_MIN # Store this for later use to handle fading out.

#local variables
ES_PROCESS = "emulationstatio"

#TODO: Fill in all of the current RetroPie Emulator process names in this list.
EMU_PROCESS_LIST = ["advmame","ags","alephone","atari800","basiliskll","cannonball","capricerpi","cgenesis","daphne","dgen","dosbox","eduke32","fbzx","frotz","fuse","gemrb","gngeo","gpsp","hatari","ioquake3","jzintv","kodi","linapple","lincity","love","mame","micropolis","mupen64plus","openbor","openmsx","openttd","opentyrian","osmose","pifba","pisnes","ppsspp","reicast","residualvm","retroarch","scummvm","sdlpop","simcoupe","snes9x","solarus","stella","stratagus","tyrquake","uae4all2","uae4arm","uqm","vice","wolf4sdl","xrick","xroar","zdoom"]

# LOGGING SETUP
SCRIPT_NAME = os.path.basename(__file__)
LOG_DIR = os.path.dirname(os.path.abspath(__file__)) + "/logs/"
LOG_FILE = LOG_DIR + SCRIPT_NAME[:-3] + ".log"
print(SCRIPT_NAME)
print(LOG_DIR)
print(LOG_FILE)
if not os.path.exists(os.path.dirname(LOG_DIR)):
    print(LOG_DIR+" not exists")
    os.makedirs(os.path.dirname(LOG_DIR))
if os.path.isfile(LOG_FILE):
    print(LOG_FILE+" copy")
    move(LOG_FILE, LOG_FILE+".bak")
logging.basicConfig( filename=LOG_FILE, level=logging.INFO )

##############################################################################

def log( message ):
    now = datetime.now().strftime("[%Y-%m-%d][%H:%M:%S]")
    logging.info( now +" "+ message )

def adjustVolume( newVolume ):
    global mixer
    mixer.music.set_volume( newVolume )
    log(">> newVolume ["+str(mixer.music.get_volume())+"]")
    
def startSong(forceStart):
    global RESTART_MODE, mixer
    if RESTART_MODE or forceStart:
        mixer.music.rewind() #testing
        mixer.music.play()
        log(">> Audio started")
    else:
        mixer.music.unpause()
        log(">> Audio resumed")

def stopSong():
    global RESTART_MODE, mixer
    if RESTART_MODE:
        mixer.music.stop() 
        log(">> Audio stopped")
    else:
        mixer.music.pause() 
        log(">> Audio paused")

def fadeVolumeUp(forceStart):
    global VOLUME_FADE_RATE, VOLUME_MAX, VOLUME_MIN
    currVolume = VOLUME_MIN
    adjustVolume( currVolume )
    startSong(forceStart)
    log("VolumeUp to "+str(VOLUME_MAX)+" [starting volume="+str(currVolume)+"]")
    while not ( currVolume >= VOLUME_MAX ):
        currVolume += VOLUME_FADE_RATE
        adjustVolume( currVolume )
        time.sleep( VOLUME_FADE_DELAY )
    adjustVolume( VOLUME_MAX )

def fadeVolumeDown():
    global VOLUME_FADE_RATE, VOLUME_MAX, VOLUME_MIN
    currVolume = VOLUME_MAX
    adjustVolume( currVolume )
    log("VolumeDown to "+str(VOLUME_MIN)+" [starting volume="+str(currVolume)+"]")
    while not ( currVolume <= VOLUME_MIN ):
        currVolume -= VOLUME_FADE_RATE
        adjustVolume( currVolume )
        time.sleep( VOLUME_FADE_DELAY )
    adjustVolume( VOLUME_MIN )
    stopSong()

log("Script: "+SCRIPT_NAME)
log("LOGDIR: "+LOG_DIR)
log("LOGFIL: "+LOG_FILE)

##############################################################################
        
log("\n*********************\n** EXECUTION START **\n*********************")

#test: Ran into some issues with script crashing on a cold boot, so we're camping for emulationstation (if ES can start, so can we!)
esIsRunning = False
while not esIsRunning:
    log("Waiting for EmulationStation to start...")
    time.sleep(1)
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    for pid in pids:
        try:
            procname = open(os.path.join('/proc',pid,'comm'),'rb').read()
            if procname[:-1] == ES_PROCESS: # Emulation Station's actual process name is apparently short 1 letter.
                esIsRunning=True
        except IOError: 
            continue

#ES Should be going, see if we need to delay our start

if startdelay > 0:
    log("Delaying music Start by "+startdelay+" seconds")
    time.sleep(startdelay) # Delay audio start per config option above
    
#Look for OMXplayer - if it's running, someone's got a splash screen going!
log("Checking for splashscreen video [OMXplayer]")
pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
for pid in pids:
    try:
        procname = open(os.path.join('/proc',pid,'comm'),'rb').read()
        #videoPlayer = ["omxplayer","omxplayer.bin"]
        if procname[:-1] == "omxplayer" or procname[:-1] == "omxplayer.bin": # Looking for a splash screen!
            log("Waiting for splashscreen video to end... [OMXplayer]")
            while os.path.exists('/proc/'+pid):
                time.sleep(1) #OMXPlayer is running, sleep 1 to prevent the need for a splash.
    except IOError: 
        continue
        
# If startsong specified, always use it
if not startsong == "":
    log("startsong specified ["+startsong+"]")
    try:
        currentSongIndex = MUSIC_LIST.index(startsong)
    except:
        currentSongIndex = -1 #If this triggers, you probably screwed up the filename, because our startsong wasn't found in the list.

#This is where the magic happens.
log("Starting main sequence...")
while True:
    while not esIsRunning: #New check (4/23/16) - Make sure EmulationStation is actually started.  There is code further down that, as part of the emulator loop, makes sure eS is running.
        log("EmulationStation shutdown. Waiting for the process to appear again (F4'd ?)")
        if mixer.music.get_busy():
            #mixer.music.stop(); #halt the music, emulationStation is not running!
            fadeVolumeDown()
        time.sleep(10)
        pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
        for pid in pids:
            try:
                procname = open(os.path.join('/proc',pid,'comm'),'rb').read()
                if procname[:-1] == ES_PROCESS: # Emulation Station's actual process name is apparently short 1 letter.
                    esIsRunning=True # Will cause us to break out of the loop because ES is now running.
            except IOError: 
                continue

    if not mixer.music.get_busy(): # We aren't currently playing any music
        while currentSongIndex == lastsong and len( MUSIC_LIST ) > 1:   #If we have more than one music, choose a new one until we get one that isn't what we just played.
            currentSongIndex = random.randint( 0, len( MUSIC_LIST ) - 1 )
        song = os.path.join(MUSIC_DIR, MUSIC_LIST[currentSongIndex])
        mixer.music.load(song)
        lastsong=currentSongIndex
        fadeVolumeUp(forceStart=True)
        log("Now Playing [" + song+"]")
        
    #Emulator check
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()] 
    emulator = -1;
    esIsRunning=False #New check 4-23-16 - set this to False (assume ES is no longer running until proven otherwise)
    for pid in pids:
        try:
            procname = open(os.path.join('/proc',pid,'comm'),'rb').read()
            if procname[:-1] == ES_PROCESS: # Killing 2 birds with one stone, while we look for emulators, make sure EmulationStation is still running.
                esIsRunning=True # And turn it back to True, because it wasn't done running.  This will prevent the loop above from stopping the music.

            if procname[:-1] in EMU_PROCESS_LIST: #If the process name is in our list of known emulators
                emulator = pid;
                #Turn down the music
                log("Emulator started ['"+procname[:-1]+"']")
                fadeVolumeDown()

                log("Monitoring emulator state ['"+procname[:-1]+"']")
                while os.path.exists("/proc/" + pid):
                    time.sleep(1); # Delay 1 second and check again.
                #Turn up the music
                log("Emulator finished ['"+procname[:-1]+"']")
                fadeVolumeUp(forceStart=False)

        except IOError: #proc has already terminated, ignore.
            continue

    time.sleep(1);
    #end of the main while loop
    
log("An error has occurred that has stopped "+SCRIPT_NAME+" from executing.") #theoretically you should never get this far.
