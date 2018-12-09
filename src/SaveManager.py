#!/usr/bin/python

import os
from scp import SCPClient
from paramiko import SSHClient
from paramiko import SFTPClient
from paramiko import AutoAddPolicy
import hashlib
import sys
import argparse


class SaveManager:
    bar_0 = "-"
    bar_1 = ">"
    bar_w = 20

    file_backup_complete = "-Backedup-"
    file_restore_complete = "-Restored-"
    file_action_not_required = "-"

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

    ssh = None
    sftp = None
    scp = None

    backup = False
    restore = False

    def get_client(self):
        self.ssh = SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())
        self.ssh.connect(self.ip, 22, 'pi')
        self.sftp = SFTPClient.from_transport(self.ssh.get_transport())
        self.scp = SCPClient(self.ssh.get_transport(), progress=self.progress)

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
                if self.md5_no_diff(game_file, pc_states_emu_home, pi_states_emu_home):
                    self.print_not_required(game_file)
                else:
                    self.copy_from_remote_to_local(
                        pi_states_emu_home + game_file,
                        pc_states_emu_home + game_file
                    )

            game_files = self.get_remote_files(pi_saves_emu_home)
            for game_file in game_files:
                if self.md5_no_diff(game_file, pc_saves_emu_home, pi_saves_emu_home):
                    self.print_not_required(game_file)
                else:
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
                if self.md5_no_diff(game_file, pc_states_emu_home, pi_states_emu_home):
                    self.print_not_required(game_file)
                else:
                    self.copy_from_local_to_remote(
                        pc_states_emu_home + game_file,
                        pi_states_emu_home + game_file
                    )

            game_files = self.get_local_files(pc_saves_emu_home)
            for game_file in game_files:
                if self.md5_no_diff(game_file, pc_saves_emu_home, pi_saves_emu_home):
                    self.print_not_required(game_file)
                else:
                    self.copy_from_local_to_remote(
                        pc_saves_emu_home + game_file,
                        pi_saves_emu_home + game_file
                    )

    def print_not_required(self, game_file):
        print("\r | {:>} | {:^10} | {}".format(self.bar_1 * self.bar_w, self.file_action_not_required, game_file))

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

    def md5_no_diff(self, game_file, pc_states_emu_home, pi_states_emu_home):
        md5_local = self.get_local_md5sum(pc_states_emu_home + game_file)
        md5_remote = self.get_remote_md5sum(pi_states_emu_home + game_file)
        return md5_local == md5_remote

    def get_local_md5sum(self, path):
        hash_obj = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()

    def get_remote_md5sum(self, path):
        _, raw_out, _ = self.ssh.exec_command("md5sum \"{}\"".format(path))
        return str(self.get_first_element(raw_out)).split(" ", 1)[0]

    def get_first_element(self, raw_out):
        try:
            return raw_out.read().splitlines()[0]
        except IndexError:
            return 0


if __name__ == '__main__':
    SaveManager()
