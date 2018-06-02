import datetime
import os
import time


#####################################################

def get_process_ids():
    return [pid for pid in os.listdir('/proc') if pid.isdigit()]


def get_process_name(pid):
    try:
        return open(os.path.join('/proc', pid, 'comm'), 'rb').read()[:-1]  # Remove last character (new line)
    except IOError:
        return "null"


def get_current_sorted_process_names():
    return sorted(set([get_process_name(pid) for pid in get_process_ids()]))


def get_added_processes(set_new, set_old):
    return [i for i in set_new if not i in set_old]


def get_removed_processes(set_new, set_old):
    return [i for i in set_old if not i in set_new]


#####################################################

oldSet = get_current_sorted_process_names()

while True:
    time.sleep(1)
    newSet = get_current_sorted_process_names()

    addedSet = get_added_processes(newSet, oldSet)
    removedSet = get_removed_processes(newSet, oldSet)

    if addedSet or removedSet:
        print("\n(Processes: " + str(len(newSet)) + ")\t{:%H:%M:%S}".format(datetime.datetime.now()))
        if addedSet:
            print(" + " + str(addedSet))
        if removedSet:
            print(" - " + str(removedSet))

    oldSet = newSet

#####################################################
