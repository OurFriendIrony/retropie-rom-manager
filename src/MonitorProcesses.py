import datetime
import os
import time


def get_process_ids():
    return [pid for pid in os.listdir('/proc') if pid.isdigit()]


def get_process_name(pid):
    try:
        return open(os.path.join('/proc', pid, 'comm'), 'rb').read()[:-1]  # Remove last character (new line)
    except IOError:
        return "null"


def get_current_sorted_process_names():
    return sorted(set([get_process_name(pid) for pid in get_process_ids()]))


def get_added_processes(old_set, new_set):
    return [i for i in new_set if not i in old_set]


def get_removed_processes(old_set, new_set):
    return [i for i in old_set if not i in new_set]


def main():
    old_set = get_current_sorted_process_names()

    while True:
        time.sleep(1)
        new_set = get_current_sorted_process_names()

        added_set = get_added_processes(old_set, new_set)
        removed_set = get_removed_processes(old_set, new_set)

        if added_set or removed_set:
            print("\n(Processes: " + str(len(new_set)) + ")\t{:%H:%M:%S}".format(datetime.datetime.now()))
            if added_set:
                print(" + " + str(added_set))
            if removed_set:
                print(" - " + str(removed_set))

        old_set = new_set


if __name__ == '__main__':
    main()
