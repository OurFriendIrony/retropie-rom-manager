#!/usr/bin/python

import os
from scp import SCPClient
from paramiko import SSHClient
from paramiko import AutoAddPolicy
import sys


def get_first_element(stdout):
    try:
        return stdout.read().splitlines()[0]
    except IndexError:
        return 0


bar_0 = "-"
bar_1 = ">"

state_copy_complete = "COPIED"
state_copy_skipped = "SKIPPED"
state_copy_not_required = "EXISTS"


def progress(filename, size, sent):
    diff = (float(sent) / float(size) * 100)
    bar = "{:{b}<20}".format(bar_1 * int(diff / 5), b=bar_0)

    if int(diff) == 100:
        print("\r | {:>20} | {:^10} | {}".format(bar, state_copy_complete, filename))
    else:
        sys.stdout.write("\r | {:>20} | {:^9.02f}% | {}".format(bar, diff, filename))


class RomManager:
    ip = "192.168.1.178"
    emus = [
        "atari2600", "atari7800", "nes", "snes",
        "megadrive", "gba", "n64", "dreamcast",
        "nds", "fba", "psx"
    ]

    skip_roms = {
        "atari2600": [],
        "atari7800": [],
        "nes": [],
        "snes": [],
        "megadrive": [],
        "gba": [],
        "n64": [],
        "dreamcast": [],
        "nds": [],
        "fba": [],
        "psx": []
    }

    pc_roms_home = "/media/videos/Games/{}/roms/"
    # pc_saves_home = "/media/videos/Games/{}/saves/"
    # pc_states_home = "/media/videos/Games/{}/states/"

    pi_roms_home = "/home/pi/RetroPie/roms/{}/"
    # pi_saves_home = "/home/pi/RetroPie/saves/{}/"
    # pi_states_home = "/home/pi/RetroPie/states/{}/"

    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    ssh.connect(ip, 22, 'pi')
    scp = SCPClient(ssh.get_transport(), progress=progress)

    def __init__(self):
        for emu in self.emus:
            self.print_emu_header(emu)

            game_files = self.get_local_files(self.pc_roms_home, emu)

            for game_file in game_files:
                rom_from = self.pc_roms_home.format(emu) + game_file
                rom_to = self.pi_roms_home.format(emu) + game_file

                rom_from_size = self.get_local_filesize(rom_from)
                rom_to_size = self.get_remote_filesize(rom_to)

                if self.is_skipped_rom(emu, game_file):
                    print("\r | {:{b}>20} | {:^10} | {}".format(bar_0 * 20, state_copy_skipped, game_file, b=bar_0))
                elif rom_from_size == rom_to_size:
                    print(
                        "\r | {:{b}>20} | {:^10} | {}".format(bar_1 * 20, state_copy_not_required, game_file, b=bar_0))
                else:
                    self.copy_rom(rom_from, rom_to)


    def get_local_files(self, path, emu):
        games_dir = path.format(emu)
        game_files = sorted(os.listdir(games_dir))
        return game_files

    def copy_rom(self, rom_from, rom_to):
        # 'progress' function prints output from this operation
        self.ssh.exec_command("rm \"{}\"".format(rom_to))
        self.scp.put(rom_from, rom_to)

    def is_skipped_rom(self, emu, rom):
        rom_raw = os.path.splitext(rom)[0]
        skip_roms_emu = self.skip_roms.get(emu, [])
        if "*" in skip_roms_emu:
            return True
        else:
            return rom_raw in skip_roms_emu

    def print_emu_header(self, emu):
        ll = 100
        print("__{:^{ll}}__\n| {:^{ll}} |\n'.{:^{ll}}.'".format("_" * ll, emu.upper(), "_" * ll, ll=ll))

    def get_remote_filesize(self, rom_to):
        stdin, stdout, stderr = self.ssh.exec_command("wc -c < \"{}\"".format(rom_to))
        return str(get_first_element(stdout))

    def get_local_filesize(self, rom_from):
        return str(os.stat(rom_from).st_size)


if __name__ == '__main__':
    RomManager()
