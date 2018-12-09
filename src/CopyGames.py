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


bar_char = ">"


def progress(filename, size, sent):
    diff = (float(sent) / float(size) * 100)
    bar = "{:-<20}".format(bar_char * int(diff / 5))

    if int(diff) == 100:
        print("\r| {:>20} | {:>10} | {}".format(bar, "DONE", filename))
    else:
        sys.stdout.write("\r| {:>20} | {:>9.02f}% | {}".format(bar, diff, filename))


class SaveManager:
    ip = "192.168.1.177"
    emus = [
        "atari2600", "atari7800", "nes", "snes",
        "megadrive", "gba", "n64", "dreamcast",
        "nds", "fba", "psx"
    ]

    pc_roms_home = "/media/videos/Games"
    pi_roms_home = "/home/pi/RetroPie/roms"

    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    ssh.connect(ip, 22, 'pi')
    scp = SCPClient(ssh.get_transport(), progress=progress)

    def __init__(self):
        for emu in self.emus:
            self.print_emu_header(emu)

            games_dir = "{}/{}/games/".format(self.pc_roms_home, emu)
            game_files = os.listdir(games_dir)

            for game_file in game_files:
                rom_from = self.pc_roms_home + "/" + emu + "/games/" + game_file
                rom_to = self.pi_roms_home + "/" + emu + "/" + game_file

                rom_from_size = self.get_local_filesize(rom_from)
                rom_to_size = self.get_remote_filesize(rom_to)

                if rom_from_size == rom_to_size:
                    print("| {:>20} | {:>10} | {}".format(bar_char * 20, "OK", game_file))
                else:
                    # print("{:>10} -> {:>10} | {}".format(rom_to_size, rom_from_size, game_file))
                    self.ssh.exec_command("rm \"{}\"".format(rom_to))
                    self.scp.put(rom_from, rom_to)
            print("")

    def print_emu_header(self, emu):
        ll = 100
        print("__{:^{ll}}__\n| {:^{ll}} |\n'.{:^{ll}}.'".format("_" * ll, emu.upper(), "_" * ll, ll=ll))

    def get_remote_filesize(self, rom_to):
        stdin, stdout, stderr = self.ssh.exec_command("wc -c < \"{}\"".format(rom_to))
        return str(get_first_element(stdout))

    def get_local_filesize(self, rom_from):
        return str(os.stat(rom_from).st_size)


if __name__ == '__main__':
    SaveManager()
