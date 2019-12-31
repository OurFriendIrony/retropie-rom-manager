# Scripts to support Saves and Roms backups for retropie    
  
| **License** | **Build** | **Coverage** |
|---|---|---|
| [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) | [![Build Status](https://travis-ci.org/OurFriendIrony/retropie-rom-manager.png)](https://travis-ci.org/OurFriendIrony/retropie-rom-manager) | [![codecov](https://codecov.io/gh/OurFriendIrony/retropie-rom-manager/branch/master/graph/badge.svg)](https://codecov.io/gh/OurFriendIrony/retropie-rom-manager) |
  
## Prereqs  
`pip install -r requirements.txt`  
  
## Executing Tests  
`coverage run -m pytest -v`  
  
## Scripts  
**SaveManager**  
Used to backup or restore 'save' and 'state' game files between a pi and a local disk
```
python ./src/SaveManager.py --backup
python ./src/SaveManager.py --restore
```
  
**RomManager**  
Used to copy all emulator roms from local disk to a pi
```
python ./src/RomManager.py
```

