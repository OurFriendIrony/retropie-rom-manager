#!/usr/bin/python

import os
import sys

from LRFSClient import LRFSClient


class RomManager:
    bar_h = "_"
    bar_wp = 20
    bar_wh = 100

    file_copy_complete = "-Copied-"
    file_action_skipped = "-Ignored-"
    file_action_not_required = "-"

    ip = "192.168.1.179"

    emus = [
        "atari2600", "atari7800", "nes",
        "snes", "megadrive", "gba",
        "n64", "dreamcast",
        "nds", "fba", "psx"
    ]

    skip_roms = {
        "atari2600": [], "atari7800": [], "nes": [],
        "snes": [], "megadrive": [], "gba": [],
        "n64": [], "dreamcast": [],
        "nds": [], "fba": [], "psx": []
    }

    pc_roms_home = "/media/videos/Games/{}/roms/"
    pi_roms_home = "/home/pi/RetroPie/roms/{}/"

    ssh_client = None

    def __init__(self):
        self.ssh_client = LRFSClient(self.ip, progress=self.progress)
        for emu in self.emus:
            self.restore_roms(emu)

    def restore_roms(self, emu):
        pi_roms_emu_home = self.pi_roms_home.format(emu)
        pc_roms_emu_home = self.pc_roms_home.format(emu)

        self.print_emu_header(emu)
        game_files = self.ssh_client.get_local_files(pc_roms_emu_home)
        for game_file in game_files:
            rom_from = pc_roms_emu_home + game_file
            rom_to = pi_roms_emu_home + game_file

            if self.is_skipped_rom(emu, game_file):
                self.print_action_skipped(game_file)
            elif self.no_change_required(rom_from, rom_to):
                self.print_action_not_required(game_file)
            else:
                self.ssh_client.copy_from_local_to_remote(rom_from, rom_to)

    def no_change_required(self, rom_from, rom_to):
        rom_from_size = self.ssh_client.get_local_filesize(rom_from)
        rom_to_size = self.ssh_client.get_remote_filesize(rom_to)
        return str(rom_from_size) == str(rom_to_size)

    def is_skipped_rom(self, emu, rom):
        rom_raw = os.path.splitext(rom)[0]
        skip_roms_emu = self.skip_roms.get(emu, [])
        if "*" in skip_roms_emu:
            return True
        else:
            return rom_raw in skip_roms_emu

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
            filename
        ))

    def print_action_not_required(self, filename):
        print("\r |{:^20}| {:^10} | {}".format(
            self.get_bar(100.0),
            self.file_action_not_required,
            filename
        ))

    def print_action_complete(self, filename):
        print("\r |{:^20}| {:^10} | {}".format(
            self.get_bar(100.0),
            self.file_copy_complete,
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
