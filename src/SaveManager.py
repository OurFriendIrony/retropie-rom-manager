#!/usr/bin/python

import sys
import argparse

from LRFSClient import LRFSClient


class SaveManager:
    bar_0 = "-"
    bar_1 = ">"
    bar_w = 20

    file_backup_complete = "-Backedup-"
    file_restore_complete = "-Restored-"
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
    pc_saves_home = "/media/videos/Games/{}/saves/"
    pc_states_home = "/media/videos/Games/{}/states/"

    pi_roms_home = "/home/pi/RetroPie/roms/{}/"
    pi_saves_home = "/home/pi/RetroPie/saves/{}/"
    pi_states_home = "/home/pi/RetroPie/states/{}/"

    ssh_client = None

    backup = False
    restore = False

    def __init__(self):
        self.ssh_client = LRFSClient(self.ip, progress=self.progress)

        self.parse_input()
        if self.backup:
            self.backup_saves()
        elif self.restore:
            self.restore_saves()
        else:
            print("Select exe mode passed")

    def progress(self, filename, size, sent):
        diff = (float(sent) / float(size) * 100)
        bar = "{:{b}<{w}}".format(self.bar_1 * int(diff / 5), b=self.bar_0, w=self.bar_w)
        if self.backup:
            end_state = self.file_backup_complete
        else:
            end_state = self.file_restore_complete

        if int(diff) == 100:
            print("\r | {} | {:^10} | {}".format(bar, end_state, filename))
        else:
            sys.stdout.write("\r | {} | {:^9.02f}% | {}".format(bar, diff, filename))

    def parse_input(self):
        parser = argparse.ArgumentParser(description="Manage RetroPie save files")
        parser.add_argument("--backup", dest="backup", const=True, default=False,
                            nargs="?", help="Backup all Save and State files")
        parser.add_argument("--restore", dest="restore", const=True, default=False,
                            nargs="?", help="Restore all Save and State files")
        args = parser.parse_args()
        self.backup = args.backup
        self.restore = args.restore

    def backup_saves(self):
        for emu in self.emus:
            pi_states_emu_home = self.pi_states_home.format(emu)
            pi_saves_emu_home = self.pi_saves_home.format(emu)
            pc_states_emu_home = self.pc_states_home.format(emu)
            pc_saves_emu_home = self.pc_saves_home.format(emu)

            self.print_emu_header(emu)
            game_files = self.ssh_client.get_remote_files(pi_states_emu_home)
            for game_file in game_files:
                if self.ssh_client.md5_no_diff(game_file, pc_states_emu_home, pi_states_emu_home):
                    self.print_action_not_required(game_file)
                else:
                    self.ssh_client.copy_from_remote_to_local(
                        pi_states_emu_home + game_file,
                        pc_states_emu_home + game_file
                    )

            game_files = self.ssh_client.get_remote_files(pi_saves_emu_home)
            for game_file in game_files:
                if self.ssh_client.md5_no_diff(game_file, pc_saves_emu_home, pi_saves_emu_home):
                    self.print_action_not_required(game_file)
                else:
                    self.ssh_client.copy_from_remote_to_local(
                        pi_saves_emu_home + game_file,
                        pc_saves_emu_home + game_file
                    )

    def restore_saves(self):
        for emu in self.emus:
            pi_states_emu_home = self.pi_states_home.format(emu)
            pi_saves_emu_home = self.pi_saves_home.format(emu)
            pc_states_emu_home = self.pc_states_home.format(emu)
            pc_saves_emu_home = self.pc_saves_home.format(emu)

            self.print_emu_header(emu)
            game_files = self.ssh_client.get_local_files(pc_states_emu_home)
            for game_file in game_files:
                if self.ssh_client.md5_no_diff(game_file, pc_states_emu_home, pi_states_emu_home):
                    self.print_action_not_required(game_file)
                else:
                    self.ssh_client.copy_from_local_to_remote(
                        pc_states_emu_home + game_file,
                        pi_states_emu_home + game_file
                    )

            game_files = self.ssh_client.get_local_files(pc_saves_emu_home)
            for game_file in game_files:
                if self.ssh_client.md5_no_diff(game_file, pc_saves_emu_home, pi_saves_emu_home):
                    self.print_action_not_required(game_file)
                else:
                    self.ssh_client.copy_from_local_to_remote(
                        pc_saves_emu_home + game_file,
                        pi_saves_emu_home + game_file
                    )

    def print_action_not_required(self, game_file):
        print("\r | {:>} | {:^10} | {}".format(
            self.bar_1 * self.bar_w,
            self.file_action_not_required,
            game_file
        ))

    def print_emu_header(self, emu):
        ll = 100
        print("__{:^{ll}}__\n| {:^{ll}} |\n'.{:^{ll}}.'".format(
            "_" * ll,
            emu.upper(),
            "_" * ll,
            ll=ll
        ))


if __name__ == '__main__':
    SaveManager()
