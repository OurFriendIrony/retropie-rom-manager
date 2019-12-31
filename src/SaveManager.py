#!/usr/bin/python

import os
import sys
import argparse
import yaml

from LRFSClient import LRFSClient
from ProgressManager import ProgressManager

def _str(data):
    try:
        return str(data.decode('utf-8'))
    except:
        return str(data)


class SaveManager:
    cfg_path = os.getcwd() + "/cfg/cfg.yml"
    cfg = None

    ssh_client = None

    def __init__(self):
        with open(self.cfg_path, 'r') as stream:
            self.cfg = yaml.safe_load(stream)
        backup, restore = self.parse_input()

        if backup:
            self.pm = ProgressManager(ProgressManager.BACKEDUP)
        else:
            self.pm = ProgressManager(ProgressManager.RESTORED)

        self.ssh_client = LRFSClient(self.cfg['dest']['addr'], progress=self.pm.progress)

        for system in self.cfg['systems']:
            emu = system['emu']
            skips = system['skip_roms']
            if backup:
                self.backup_saves(emu, skips)
            else:
                self.restore_saves(emu, skips)

    def parse_input(self):
        parser = argparse.ArgumentParser(description="Manage RetroPie save files")
        parser.add_argument("--backup", dest="backup", const=True, default=False,
                            nargs="?", help="Backup all Save and State files")
        parser.add_argument("--restore", dest="restore", const=True, default=False,
                            nargs="?", help="Restore all Save and State files")
        args = parser.parse_args()
        return args.backup, args.restore

    def no_change_required(self, file_from, file_to):
        return self.ssh_client.md5_is_equal(file_from, file_to)

    def backup_saves(self, emu, skips=[]):
        pi_states_emu_home = self.cfg['dest']['dirs']['states'].format(emu)
        pi_saves_emu_home = self.cfg['dest']['dirs']['saves'].format(emu)
        pc_states_emu_home = self.cfg['source']['dirs']['states'].format(emu)
        pc_saves_emu_home = self.cfg['source']['dirs']['saves'].format(emu)

        self.pm.print_emu_header(emu, "Backup States")
        game_files = self.ssh_client.get_remote_files(pi_states_emu_home)
        for game_file in game_files:
            file_from = pi_states_emu_home + game_file
            file_to = pc_states_emu_home + game_file

            if self.is_skipped_rom(game_file, skips):
                self.pm.print_action_skipped(game_file)
            elif self.no_change_required(file_to, file_from):
                self.pm.print_action_not_required(game_file)
            else:
                self.ssh_client.copy_from_remote_to_local(file_from, file_to)

        self.pm.print_emu_header(emu, "Backup Saves")
        game_files = self.ssh_client.get_remote_files(pi_saves_emu_home)
        for game_file in game_files:
            file_to = pc_saves_emu_home + game_file
            file_from = pi_saves_emu_home + game_file

            if self.is_skipped_rom(game_file, skips):
                self.pm.print_action_skipped(game_file)
            elif self.no_change_required(file_to, file_from):
                self.pm.print_action_not_required(game_file)
            else:
                self.ssh_client.copy_from_remote_to_local(file_from, file_to)

    def restore_saves(self, emu, skips=[]):
        pi_states_emu_home = self.cfg['dest']['dirs']['states'].format(emu)
        pi_saves_emu_home = self.cfg['dest']['dirs']['saves'].format(emu)
        pc_states_emu_home = self.cfg['source']['dirs']['states'].format(emu)
        pc_saves_emu_home = self.cfg['source']['dirs']['saves'].format(emu)

        self.pm.print_emu_header(emu, "Restore States")
        try:
            game_files = self.ssh_client.get_local_files(pc_states_emu_home)
            for game_file in game_files:
                file_from = pc_states_emu_home + game_file
                file_to = pi_states_emu_home + game_file

                if self.is_skipped_rom(game_file, skips):
                    self.pm.print_action_skipped(game_file)
                elif self.no_change_required(file_from, file_to):
                    self.pm.print_action_not_required(game_file)
                else:
                    self.ssh_client.copy_from_local_to_remote(file_from, file_to)
        except:
            self.pm.print_action_not_required("-- No State Dir --")

        self.pm.print_emu_header(emu, "Restore Saves")
        try:
            game_files = self.ssh_client.get_local_files(pc_saves_emu_home)
            for game_file in game_files:
                file_from = pc_saves_emu_home + game_file
                file_to = pi_saves_emu_home + game_file

                if self.is_skipped_rom(game_file, skips):
                    self.pm.print_action_skipped(game_file)
                elif self.no_change_required(file_from, file_to):
                    self.pm.print_action_not_required(game_file)
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


if __name__ == '__main__':
    SaveManager()


