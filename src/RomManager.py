#!/usr/bin/python

import os
import sys
import yaml

from LRFSClient import LRFSClient

def _str(data):
    try:
        return str(data.decode('utf-8'))
    except:
        return str(data)


class RomManager:
    bar_h = "_"
    bar_wp = 20
    bar_wh = 100

    file_copy_complete = "-Copied-"
    file_action_skipped = "-Ignored-"
    file_action_not_required = "-"

    cfg_path = os.getcwd() + "/cfg/cfg.yml"
    cfg = None

    ssh_client = None

    def __init__(self):
        with open(self.cfg_path, 'r') as stream:
            self.cfg = yaml.safe_load(stream)
        self.ssh_client = LRFSClient(self.cfg['dest']['addr'], progress=self.progress)
        for system in self.cfg['systems']:
            emu = system['emu']
            skips = system['skip_roms']
            self.restore_roms(emu, skips)

    def restore_roms(self, emu, skips=[]):
        pi_roms_emu_home = self.cfg['dest']['dirs']['roms'].format(emu)
        pc_roms_emu_home = self.cfg['source']['dirs']['roms'].format(emu)

        self.print_emu_header(emu)
        game_files = self.ssh_client.get_local_files(pc_roms_emu_home)
        for game_file in game_files:
            rom_from = pc_roms_emu_home + game_file
            rom_to = pi_roms_emu_home + game_file

            if self.is_skipped_rom(game_file, skips):
                self.print_action_skipped(game_file)
            elif self.no_change_required(rom_from, rom_to):
                self.print_action_not_required(game_file)
            else:
                self.ssh_client.copy_from_local_to_remote(rom_from, rom_to)

    def no_change_required(self, rom_from, rom_to):
        rom_from_size = self.ssh_client.get_local_filesize(rom_from)
        rom_to_size = self.ssh_client.get_remote_filesize(rom_to)
        return _str(rom_from_size) == _str(rom_to_size)

    def is_skipped_rom(self, rom, skip_roms):
        rom_raw = os.path.splitext(rom)[0]
        if "*" in skip_roms:
            return True
        else:
            return rom_raw in skip_roms

    def print_emu_header(self, emu):
        print("__{:^{ll}}__\n| {:^{ll}} |\n'.{:^{ll}}.'".format(
            self.bar_h * self.bar_wh,
            emu.upper(),
            self.bar_h * self.bar_wh,
            ll=self.bar_wh
        ))

    def print_action_skipped(self, filename):
        print("\r |{:^20}| {:^10} | {}".format(
            "n/a",
            self.file_action_skipped,
            self.bts(filename)
        ))

    def print_action_not_required(self, filename):
        print("\r |{:^20}| {:^10} | {}".format(
            self.get_bar(100.0),
            self.file_action_not_required,
            self.bts(filename)
        ))

    def print_action_complete(self, filename):
        print("\r |{:^20}| {:^10} | {}".format(
            self.get_bar(100.0),
            self.file_copy_complete,
            self.bts(filename)
        ))

    def print_action_progress(self, diff, filename):
        sys.stdout.write("\r |{:^20}| {:^9.02f}% | {}".format(
            self.get_bar(diff),
            diff,
            self.bts(filename)
        ))

    def progress(self, filename, size, sent):
        diff = (float(sent) / float(size) * 100)
        if int(diff) == 100:
            self.print_action_complete(_str(filename))
        else:
            self.print_action_progress(diff, _str(filename))

    def get_bar(self, diff):
        len_1 = int(diff / 5)
        len_2 = 1 - int(diff / self.bar_wh)
        return "{:20}".format(("=" * len_1) + (">" * len_2))

    def bts(self, s):
        #bytes to strings
        if isinstance(s, bytes):
            return s.decode()
        return s

if __name__ == '__main__':
    RomManager()

