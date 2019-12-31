#!/usr/bin/python

import os
import sys
import yaml


from LRFSClient import LRFSClient
from ProgressManager import ProgressManager

def _str(data):
    try:
        return str(data.decode('utf-8'))
    except:
        return str(data)


class RomManager:
    cfg_path = os.getcwd() + "/cfg/cfg.yml"
    cfg = None

    ssh_client = None

    def __init__(self):
        with open(self.cfg_path, 'r') as stream:
            self.cfg = yaml.safe_load(stream)
        self.pm = ProgressManager()
        self.ssh_client = LRFSClient(self.cfg['dest']['addr'], progress=self.pm.progress)
        for system in self.cfg['systems']:
            emu = system['emu']
            skips = system['skip_roms']
            self.restore_roms(emu, skips)

    def restore_roms(self, emu, skips=[]):
        pi_roms_emu_home = self.cfg['dest']['dirs']['roms'].format(emu)
        pc_roms_emu_home = self.cfg['source']['dirs']['roms'].format(emu)

        self.pm.print_emu_header(emu)
        game_files = self.ssh_client.get_local_files(pc_roms_emu_home)
        for game_file in game_files:
            rom_from = pc_roms_emu_home + game_file
            rom_to = pi_roms_emu_home + game_file

            if self.is_skipped_rom(game_file, skips):
                self.pm.print_action_skipped(game_file)
            elif self.no_change_required(rom_from, rom_to):
                self.pm.print_action_not_required(game_file)
            else:
                self.ssh_client.copy_from_local_to_remote(rom_from, rom_to)

    def no_change_required(self, rom_from, rom_to):
        rom_from_size = self.ssh_client.get_local_filesize(rom_from)
        rom_to_size = self.ssh_client.get_remote_filesize(rom_to)
        return _str(rom_from_size) == _str(rom_to_size)

    def is_skipped_rom(self, rom, skip_roms):
        rom_raw = os.path.splitext(rom)[0]
        if "*" in skip_roms:
            return True
        else:
            return rom_raw in skip_roms


if __name__ == '__main__':
    RomManager()


