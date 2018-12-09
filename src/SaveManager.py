#!/usr/bin/python

import sys
import argparse

from LRFSClient import LRFSClient


class SaveManager:
    bar_h = "_"
    bar_wp = 20
    bar_wh = 100

    file_backup_complete = "-Backedup-"
    file_restore_complete = "-Restored-"
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
        for emu in self.emus:
            if self.backup:
                self.backup_saves(emu)
            elif self.restore:
                self.restore_saves(emu)
            else:
                print("Select exe mode passed")

    def parse_input(self):
        parser = argparse.ArgumentParser(description="Manage RetroPie save files")
        parser.add_argument("--backup", dest="backup", const=True, default=False,
                            nargs="?", help="Backup all Save and State files")
        parser.add_argument("--restore", dest="restore", const=True, default=False,
                            nargs="?", help="Restore all Save and State files")
        args = parser.parse_args()
        self.backup = args.backup
        self.restore = args.restore

    def backup_saves(self, emu):
        pi_states_emu_home = self.pi_states_home.format(emu)
        pi_saves_emu_home = self.pi_saves_home.format(emu)
        pc_states_emu_home = self.pc_states_home.format(emu)
        pc_saves_emu_home = self.pc_saves_home.format(emu)

        self.print_emu_header(emu)
        game_files = self.ssh_client.get_remote_files(pi_states_emu_home)
        for game_file in game_files:
            if self.ssh_client.md5_is_equal(game_file, pc_states_emu_home, pi_states_emu_home):
                self.print_action_not_required(game_file)
            else:
                self.ssh_client.copy_from_remote_to_local(
                    pi_states_emu_home + game_file,
                    pc_states_emu_home + game_file
                )

        game_files = self.ssh_client.get_remote_files(pi_saves_emu_home)
        for game_file in game_files:
            if self.ssh_client.md5_is_equal(game_file, pc_saves_emu_home, pi_saves_emu_home):
                self.print_action_not_required(game_file)
            else:
                self.ssh_client.copy_from_remote_to_local(
                    pi_saves_emu_home + game_file,
                    pc_saves_emu_home + game_file
                )

    def restore_saves(self, emu):
        pi_states_emu_home = self.pi_states_home.format(emu)
        pi_saves_emu_home = self.pi_saves_home.format(emu)
        pc_states_emu_home = self.pc_states_home.format(emu)
        pc_saves_emu_home = self.pc_saves_home.format(emu)

        self.print_emu_header(emu)
        game_files = self.ssh_client.get_local_files(pc_states_emu_home)
        for game_file in game_files:
            if self.ssh_client.md5_is_equal(game_file, pc_states_emu_home, pi_states_emu_home):
                self.print_action_not_required(game_file)
            else:
                self.ssh_client.copy_from_local_to_remote(
                    pc_states_emu_home + game_file,
                    pi_states_emu_home + game_file
                )

        game_files = self.ssh_client.get_local_files(pc_saves_emu_home)
        for game_file in game_files:
            if self.ssh_client.md5_is_equal(game_file, pc_saves_emu_home, pi_saves_emu_home):
                self.print_action_not_required(game_file)
            else:
                self.ssh_client.copy_from_local_to_remote(
                    pc_saves_emu_home + game_file,
                    pi_saves_emu_home + game_file
                )

    def print_emu_header(self, emu):
        print("__{:^{ll}}__\n| {:^{ll}} |\n'.{:^{ll}}.'".format(
            self.bar_h * self.bar_wh,
            emu.upper(),
            self.bar_h * self.bar_wh,
            ll=self.bar_wh
        ))

    def print_action_not_required(self, filename):
        print("\r |{:^20}| {:^10} | {}".format(
            self.get_bar(100.0),
            self.file_action_not_required,
            filename
        ))

    def print_action_complete(self, end_state, filename):
        print("\r |{:^20}| {:^10} | {}".format(
            self.get_bar(100.0),
            end_state,
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

        if self.backup:
            end_state = self.file_backup_complete
        else:
            end_state = self.file_restore_complete

        if int(diff) == 100:
            self.print_action_complete(end_state, filename)
        else:
            self.print_action_progress(diff, filename)

    def get_bar(self, diff):
        len_1 = int(diff / 5)
        len_2 = 1 - int(diff / self.bar_wh)
        return "{:20}".format(("=" * len_1) + (">" * len_2))


if __name__ == '__main__':
    SaveManager()
