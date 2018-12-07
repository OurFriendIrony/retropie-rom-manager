#!/usr/bin/python

import argparse
import shutil
import zipfile


class SaveManager:
    RETROPIE_HOME = "/home/pi/RetroPie"

    SAVES_LOCATION = "%s/saves/" % RETROPIE_HOME
    SAVES_ZIP_OUT = "saves"

    STATES_LOCATION = "%s/states/" % RETROPIE_HOME
    STATES_ZIP_OUT = "saves"

    backup = False
    restore = False

    def __init__(self):
        self.parse_input()
        if self.backup:
            self.backup_saves()

        if self.restore:
            self.restore_saves()

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

    def unzip(self, from_file, to_dir):
        zipfilepath = ("%s.zip" % from_file)
        zip = zipfile.ZipFile(zipfilepath)
        zip.extractall(to_dir)
        zip.close()

    def backup_saves(self):
        shutil.make_archive(self.SAVES_ZIP_OUT, 'zip', self.SAVES_LOCATION)
        shutil.make_archive(self.STATES_ZIP_OUT, 'zip', self.STATES_LOCATION)

    def restore_saves(self):
        self.unzip(self.SAVES_ZIP_OUT, self.SAVES_LOCATION)
        self.unzip(self.STATES_ZIP_OUT, self.STATES_LOCATION)


if __name__ == '__main__':
    SaveManager()
