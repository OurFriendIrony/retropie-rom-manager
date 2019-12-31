#!/usr/bin/python

import os
import hashlib

from scp import SCPClient
from paramiko import SSHClient
from paramiko import SFTPClient
from paramiko import AutoAddPolicy

def _str(data):
    try:
        return str(data.decode('utf-8'))
    except:
        return str(data)


class LRFSClient(object):
    def __init__(self, host, port=22, user='pi', progress=None):
        self.ssh = SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())
        self.ssh.connect(host, port, user)
        self.sftp = SFTPClient.from_transport(self.ssh.get_transport())
        self.scp = SCPClient(self.ssh.get_transport(), progress=progress)

    def get_local_files(self, games_dir):
        return sorted(os.listdir(games_dir))

    def get_remote_files(self, games_dir):
        return sorted(self.sftp.listdir(games_dir))

    def copy_from_remote_to_local(self, rom_from, rom_to):
        self.scp.get(rom_from, rom_to)

    def copy_from_local_to_remote(self, rom_from, rom_to):
        self.ssh.exec_command("rm \"{}\"".format(rom_to))
        self.scp.put(rom_from, rom_to)

    def get_local_filesize(self, path):
        return os.stat(path).st_size

    def get_remote_filesize(self, path):
        _, raw_out, _ = self.ssh.exec_command("wc -c < \"{}\"".format(path))
        return self._get_first_element(raw_out)

    def md5_is_equal(self, home_local, home_remote):
        md5_local = self._get_local_md5sum(home_local)
        md5_remote = self._get_remote_md5sum(home_remote)
        return _str(md5_local) == _str(md5_remote)

    def _get_local_md5sum(self, path):
        hash_obj = hashlib.md5()
        try:
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except IOError:
            return 0

    def _get_remote_md5sum(self, path):
        _, raw_out, _ = self.ssh.exec_command("md5sum \"{}\"".format(path))
        return str(self._get_first_element(raw_out)).split(" ", 1)[0]

    def _get_first_element(self, raw_out):
        try:
            return _str(raw_out.read()).splitlines()[0]
        except IndexError:
            return 0


