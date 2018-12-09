#!/usr/bin/python

import os
import sys

from LRFSClient import LRFSClient


class RomManager:
    bar_0 = "-"
    bar_1 = ">"
    bar_w = 20

    file_copy_complete = "-Copied-"
    file_copy_skipped = "-Ignored-"
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
            pi_roms_emu_home = self.pi_roms_home.format(emu)
            pc_roms_emu_home = self.pc_roms_home.format(emu)

            self.print_emu_header(emu)
            game_files = self.ssh_client.get_local_files(pc_roms_emu_home)
            for game_file in game_files:
                rom_from = pc_roms_emu_home + game_file
                rom_to = pi_roms_emu_home + game_file

                if self.is_skipped_rom(emu, game_file):
                    print("\r | {:{b}>20} | {:^10} | {}".format(
                        self.bar_0 * 20, self.file_copy_skipped,
                        game_file, b=self.bar_0
                    ))
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
        ll = 100
        print("__{:^{ll}}__\n| {:^{ll}} |\n'.{:^{ll}}.'".format(
            "_" * ll,
            emu.upper(),
            "_" * ll,
            ll=ll
        ))

    def print_action_not_required(self, game_file):
        print("\r | {:{b}>20} | {:^10} | {}".format(
            self.bar_1 * self.bar_w,
            self.file_action_not_required,
            game_file, b=self.bar_0
        ))

    def progress(self, filename, size, sent):
        diff = (float(sent) / float(size) * 100)
        bar = "{:{b}<20}".format(self.bar_1 * int(diff / 5), b=self.bar_0)

        if int(diff) == 100:
            print("\r | {:>20} | {:^10} | {}".format(bar, self.file_copy_complete, filename))
        else:
            sys.stdout.write("\r | {:>20} | {:^9.02f}% | {}".format(bar, diff, filename))


if __name__ == '__main__':
    RomManager()
