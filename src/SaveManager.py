#!/usr/bin/python

import os
from scp import SCPClient
from paramiko import SSHClient
from paramiko import SFTPClient
from paramiko import AutoAddPolicy
import sys
import argparse


class SaveManager:
    bar_0 = "-"
    bar_1 = ">"

    state_copy_backup_complete = "BACKED-UP"
    state_copy_restore_complete = "RESTORED"

    state_copy_skipped = "SKIPPED"
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
    pc_saves_home = "/media/videos/Games/{}/saves/"
    pc_states_home = "/media/videos/Games/{}/states/"

    pi_roms_home = "/home/pi/RetroPie/roms/{}/"
    pi_saves_home = "/home/pi/RetroPie/saves/{}/"
    pi_states_home = "/home/pi/RetroPie/states/{}/"

    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    ssh.connect(ip, 22, 'pi')
    scp = None
    sftp = SFTPClient.from_transport(ssh.get_transport())

    backup = False
    restore = False

    def get_client(self):
        self.scp = SCPClient(self.ssh.get_transport(), progress=self.progress)

    def progress(self, filename, size, sent):
        diff = (float(sent) / float(size) * 100)
        bar = "{:{b}<20}".format(self.bar_1 * int(diff / 5), b=self.bar_0)
        if self.backup:
            end_state = self.state_copy_backup_complete
        else:
            end_state = self.state_copy_restore_complete

        if int(diff) == 100:
            print("\r | {:>20} | {:^10} | {}".format(bar, end_state, filename))
        else:
            sys.stdout.write("\r | {:>20} | {:^9.02f}% | {}".format(bar, diff, filename))

    def parse_input(self):
        parser = argparse.ArgumentParser(description="Manage RetroPie save files")
        parser.add_argument("--backup", dest="backup", const=True, default=False,
                            nargs="?", help="Backup all Save and State files")
        parser.add_argument("--restore", dest="restore", const=True, default=False,
                            nargs="?", help="Restore all Save and State files")
        args = parser.parse_args()
        self.backup = args.backup
        if self.backup:
            self.restore = False
        else:
            self.restore = args.restore

    def __init__(self):
        self.get_client()
        self.parse_input()
        if self.backup:
            self.backup_saves()
        elif self.restore:
            self.restore_saves()
        else:
            print("Select exe mode passed")

    def backup_saves(self):
        for emu in self.emus:
            pi_states_emu_home = self.pi_states_home.format(emu)
            pi_saves_emu_home = self.pi_saves_home.format(emu)
            pc_states_emu_home = self.pc_states_home.format(emu)
            pc_saves_emu_home = self.pc_saves_home.format(emu)

            self.print_emu_header(emu)
            game_files = self.get_remote_files(pi_states_emu_home)
            for game_file in game_files:
                self.copy_from_remote_to_local(
                    pi_states_emu_home + game_file,
                    pc_states_emu_home + game_file
                )

            game_files = self.get_remote_files(pi_saves_emu_home)
            for game_file in game_files:
                self.copy_from_remote_to_local(
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
            game_files = self.get_local_files(pc_states_emu_home)
            for game_file in game_files:
                self.copy_from_local_to_remote(
                    pc_states_emu_home + game_file,
                    pi_states_emu_home + game_file
                )

            game_files = self.get_local_files(pc_saves_emu_home)
            for game_file in game_files:
                self.copy_from_local_to_remote(
                    pc_saves_emu_home + game_file,
                    pi_saves_emu_home + game_file
                )

    def print_emu_header(self, emu):
        ll = 100
        print("__{:^{ll}}__\n| {:^{ll}} |\n'.{:^{ll}}.'".format("_" * ll, emu.upper(), "_" * ll, ll=ll))

    def get_local_files(self, games_dir):
        return sorted(os.listdir(games_dir))

    def get_remote_files(self, games_dir):
        return sorted(self.sftp.listdir(games_dir))

    def copy_from_remote_to_local(self, rom_from, rom_to):
        self.scp.get(rom_from, rom_to)

    def copy_from_local_to_remote(self, rom_from, rom_to):
        self.scp.put(rom_from, rom_to)

    def get_local_filesize(self, path):
        return os.stat(path).st_size

    def get_remote_filesize(self, path):
        _, raw_out, _ = self.ssh.exec_command("wc -c < \"{}\"".format(path))
        return self.get_first_element(raw_out)

    def get_first_element(self, raw_out):
        try:
            return raw_out.read().splitlines()[0]
        except IndexError:
            return 0


if __name__ == '__main__':
    SaveManager()
