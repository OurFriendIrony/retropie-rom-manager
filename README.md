# Scripts to support retropie    
  
| **Build** | **Coverage** |
|---|---|
| [![Build Status](https://travis-ci.org/OurFriendIrony/retropie-rom-manager.png)](https://travis-ci.org/OurFriendIrony/retropie-rom-manager) | [![codecov](https://codecov.io/gh/OurFriendIrony/retropie-rom-manager/branch/master/graph/badge.svg)](https://codecov.io/gh/OurFriendIrony/retropie-rom-manager) |
  
## Prereqs  
`pip install -r requirements.txt`  
  
## Executing Tests  
`coverage run -m pytest -v`  
  
## Scripts  
**SaveManager**  
Used to backup or restore 'save' and 'state' game files between a pi and a local disk
```
python ./src/SaveManager --backup
python ./src/SaveManager --restore
```
  
**RomManager**  
Used to copy all emulator roms from local disk to a pi
```
python ./src/RomManager
```

