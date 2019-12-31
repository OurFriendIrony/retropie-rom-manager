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
    CHAR_HEADER     = "_"
    WIDTH_PROGRESS  = 45
    WIDTH_STATUS    = 10
    WIDTH_STATUS_F  = str(WIDTH_STATUS-1)+'.02f'
    WIDTH_HEADER    = 100

    COPIED       = "-Copied-"
    BACKEDUP     = "-Backedup-"
    RESTORED     = "-Restored-"
    SKIPPED      = "-Ignored-"
    NOT_REQUIRED = "-"

    def __init__(self, end_state=None):
        if end_state:
            self.end_state = end_state
        else:
            self.end_state = self.COPIED

    def print_emu_header(self, emu, subheader=None):
        if subheader:
            print("__{:^{ll}}__\n| {:^{ll}} |\n'.{:^{ll}}.'".format(
                self.CHAR_HEADER * self.WIDTH_HEADER,
                "{} [{}]".format(emu.upper(), subheader),
                self.CHAR_HEADER * self.WIDTH_HEADER,
                ll=self.WIDTH_HEADER
            ))
        else:
            print("__{:^{ll}}__\n| {:^{ll}} |\n'.{:^{ll}}.'".format(
                self.CHAR_HEADER * self.WIDTH_HEADER,
                emu.upper(),
                self.CHAR_HEADER * self.WIDTH_HEADER,
                ll=self.WIDTH_HEADER
            ))

    def print_action_skipped(self, filename):
        w1=str(self.WIDTH_PROGRESS)
        w2=str(self.WIDTH_STATUS)
        line="\r |{:^"+w1+"}| {:^"+w2+"} | {}"
        print(
            line.format(
                "n/a",
                self.SKIPPED,
                filename
            )
        )

    def print_action_not_required(self, filename):
        w1=str(self.WIDTH_PROGRESS)
        w2=str(self.WIDTH_STATUS)
        line="\r |{:^"+w1+"}| {:^"+w2+"} | {}"
        print(
            line.format(
                self.get_bar(100.0),
                self.NOT_REQUIRED,
                filename
            )
        )

    def print_action_complete(self, filename):
        w1=str(self.WIDTH_PROGRESS)
        w2=str(self.WIDTH_STATUS)
        line="\r |{:^"+w1+"}| {:^"+w2+"} | {}"
        print(
            line.format(
                self.get_bar(100.0),
                self.end_state,
                filename
            )
        )

    def print_action_progress(self, diff, filename):
        w1=str(self.WIDTH_PROGRESS)
        w2=str(self.WIDTH_STATUS_F)
        line="\r |{:^"+w1+"}| {:^"+w2+"}% | {}"
        sys.stdout.write(
            line.format(
                self.get_bar(diff),
                diff,
                _str(filename)
            )
        )

    def progress(self, filename, size, sent):
        diff = (float(sent) / float(size) * 100)
        if int(diff) == 100:
            self.print_action_complete(filename)
        else:
            self.print_action_progress(diff, filename)

    def get_bar(self,diff):
        w1=str(self.WIDTH_PROGRESS)
        line="{:"+w1+"}"
        len_1 = int(diff * self.WIDTH_PROGRESS / 100)
        len_2 = 1 - int(diff / self.WIDTH_HEADER)
        return line.format(("=" * len_1) + (">" * len_2))


if __name__ == '__main__':
    RomManager()


