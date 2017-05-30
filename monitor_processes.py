from __future__ import print_function
import os, logging, random, time, datetime

def getProcessIds():
    return [pid for pid in os.listdir('/proc') if pid.isdigit()]

def getProcessName(pid):
    try:
        return open(os.path.join('/proc',pid,'comm'),'rb').read()[:-1] # Remove last character (new line)
    except IOError:
        return "null"
        
def getCurrentSortedProcessNames():
    return sorted( set ( [getProcessName(pid) for pid in getProcessIds()] ) )

def getAddedProcesses(newSet, oldSet):
    return [ i for i in newSet if not i in oldSet ]
    
def getRemovedProcesses(newSet, oldSet):
    return [ i for i in oldSet if not i in newSet ]

###############################################################

oldSet = getCurrentSortedProcessNames()

while True:
    time.sleep(1);
    newSet = getCurrentSortedProcessNames()
    
    addedSet = getAddedProcesses( newSet, oldSet )
    removedSet = getRemovedProcesses( newSet, oldSet )
    
    if addedSet or removedSet:
        print("\n(Processes: " + str(len(newSet)) + ")\t{:%H:%M:%S}".format(datetime.datetime.now()) )
        if addedSet:
            print( " + "+str(addedSet) )
        if removedSet:
            print( " - "+str(removedSet) )

    oldSet = newSet

###############################################################
