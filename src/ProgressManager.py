#!/usr/bin/python

import os
import sys
import yaml


def _str(data):
    try:
        return str(data.decode('utf-8'))
    except:
        return str(data)


class ProgressManager:
    bar_h = "_"
    bar_wp = 20
    bar_wh = 100

    COPIED = "-Copied-"
    BACKEDUP = "-Backedup-"
    RESTORED = "-Restored-"
    SKIPPED = "-Ignored-"
    NOT_REQUIRED = "-"

    def __init__(self, end_state=None):
        if end_state:
            self.end_state = end_state
        else:
            self.end_state = self.COPIED

    def print_emu_header(self, emu, subheader=None):
        if subheader:
            print("__{:^{ll}}__\n| {:^{ll}} |\n'.{:^{ll}}.'".format(
                self.bar_h * self.bar_wh,
                "{} [{}]".format(emu.upper(), subheader),
                self.bar_h * self.bar_wh,
                ll=self.bar_wh
            ))
        else:
            print("__{:^{ll}}__\n| {:^{ll}} |\n'.{:^{ll}}.'".format(
                self.bar_h * self.bar_wh,
                emu.upper(),
                self.bar_h * self.bar_wh,
                ll=self.bar_wh
            ))

    def print_action_skipped(self, filename):
        print("\r |{:^20}| {:^10} | {}".format(
            "n/a",
            self.SKIPPED,
            filename
        ))

    def print_action_not_required(self, filename):
        print("\r |{:^20}| {:^10} | {}".format(
            self.get_bar(100.0),
            self.NOT_REQUIRED,
            filename
        ))

    def print_action_complete(self, filename):
        print("\r |{:^20}| {:^10} | {}".format(
            self.get_bar(100.0),
            self.end_state,
            filename
        ))

    def print_action_progress(self, diff, filename):
        sys.stdout.write("\r |{:^20}| {:^9.02f}% | {}".format(
            self.get_bar(diff),
            diff,
            filename
        ))

    def progress(self, filename, size, sent):
        diff = (float(sent) / float(size) * 100)
        if int(diff) == 100:
            self.print_action_complete(filename)
        else:
            self.print_action_progress(diff, filename)

    def get_bar(self, diff):
        len_1 = int(diff / 5)
        len_2 = 1 - int(diff / self.bar_wh)
        return "{:20}".format(("=" * len_1) + (">" * len_2))


if __name__ == '__main__':
    RomManager()


