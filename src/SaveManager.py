#!/usr/bin/python

import os
import sys
import argparse
import yaml

from LRFSClient import LRFSClient

def _str(data):
    try:
        return str(data.decode('utf-8'))
    except:
        return str(data)


class SaveManager:
    bar_h = "_"
    bar_wp = 20
    bar_wh = 100

    file_backup_complete = "-Backedup-"
    file_restore_complete = "-Restored-"
    file_action_skipped = "-Ignored-"
    file_action_not_required = "-"

    cfg_path = os.getcwd() + "/cfg/cfg.yml"
    cfg = None

    ssh_client = None

    backup = False
    restore = False

    def __init__(self):
        with open(self.cfg_path, 'r') as stream:
            self.cfg = yaml.safe_load(stream)
        self.ssh_client = LRFSClient(self.cfg['dest']['addr'], progress=self.progress)
        self.parse_input()
        for system in self.cfg['systems']:
            emu = system['emu']
            skips = system['skip_roms']
            if self.backup:
                self.backup_saves(emu, skips)
            elif self.restore:
                self.restore_saves(emu, skips)
            else:
                print("Pass '--backup' or '--restore'")

    def parse_input(self):
        parser = argparse.ArgumentParser(description="Manage RetroPie save files")
        parser.add_argument("--backup", dest="backup", const=True, default=False,
                            nargs="?", help="Backup all Save and State files")
        parser.add_argument("--restore", dest="restore", const=True, default=False,
                            nargs="?", help="Restore all Save and State files")
        args = parser.parse_args()
        self.backup = args.backup
        self.restore = args.restore

    def no_change_required(self, file_from, file_to):
        return self.ssh_client.md5_is_equal(file_from, file_to)

    def backup_saves(self, emu, skips=[]):
        pi_states_emu_home = self.cfg['dest']['dirs']['states'].format(emu)
        pi_saves_emu_home = self.cfg['dest']['dirs']['saves'].format(emu)
        pc_states_emu_home = self.cfg['source']['dirs']['states'].format(emu)
        pc_saves_emu_home = self.cfg['source']['dirs']['saves'].format(emu)

        self.print_emu_header(emu, "Backup States")
        game_files = self.ssh_client.get_remote_files(pi_states_emu_home)
        for game_file in game_files:
            file_from = pi_states_emu_home + game_file
            file_to = pc_states_emu_home + game_file

            if self.is_skipped_rom(game_file, skips):
                self.print_action_skipped(game_file)
            elif self.no_change_required(file_to, file_from):
                self.print_action_not_required(game_file)
            else:
                self.ssh_client.copy_from_remote_to_local(file_from, file_to)

        self.print_emu_header(emu, "Backup Saves")
        game_files = self.ssh_client.get_remote_files(pi_saves_emu_home)
        for game_file in game_files:
            file_to = pc_saves_emu_home + game_file
            file_from = pi_saves_emu_home + game_file

            if self.is_skipped_rom(game_file, skips):
                self.print_action_skipped(game_file)
            elif self.no_change_required(file_to, file_from):
                self.print_action_not_required(game_file)
            else:
                self.ssh_client.copy_from_remote_to_local(file_from, file_to)

    def restore_saves(self, emu, skips=[]):
        pi_states_emu_home = self.cfg['dest']['dirs']['states'].format(emu)
        pi_saves_emu_home = self.cfg['dest']['dirs']['saves'].format(emu)
        pc_states_emu_home = self.cfg['source']['dirs']['states'].format(emu)
        pc_saves_emu_home = self.cfg['source']['dirs']['saves'].format(emu)

        self.print_emu_header(emu, "Restore States")
        try:
            game_files = self.ssh_client.get_local_files(pc_states_emu_home)
            for game_file in game_files:
                file_from = pc_states_emu_home + game_file
                file_to = pi_states_emu_home + game_file

                if self.is_skipped_rom(game_file, skips):
                    self.print_action_skipped(game_file)
                elif self.no_change_required(file_from, file_to):
                    self.print_action_not_required(game_file)
                else:
                    self.ssh_client.copy_from_local_to_remote(file_from, file_to)
        except:
            self.print_action_not_required("-- No State Dir --")

        self.print_emu_header(emu, "Restore Saves")
        try:
            game_files = self.ssh_client.get_local_files(pc_saves_emu_home)
            for game_file in game_files:
                file_from = pc_saves_emu_home + game_file
                file_to = pi_saves_emu_home + game_file

                if self.is_skipped_rom(game_file, skips):
                    self.print_action_skipped(game_file)
                elif self.no_change_required(file_from, file_to):
                    self.print_action_not_required(game_file)
                else:
                    self.ssh_client.copy_from_local_to_remote(file_from, file_to)
        except:
            self.print_action_not_required("-- No Save Dir --")

    def is_skipped_rom(self, rom, skip_roms):
        rom_raw = os.path.splitext(rom)[0]
        if "*" in skip_roms:
            return True
        else:
            return rom_raw in skip_roms

    def print_emu_header(self, emu, subheader=None):
        if subheader:
            print("__{:^{ll}}__\n| {:^{ll}} |\n'.{:^{ll}}.'".format(
                self.bar_h * self.bar_wh,
                "{} [{}]".format(emu.upper(), subheader),
                self.bar_h * self.bar_wh,
                ll=self.bar_wh
            ))
        else:
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


