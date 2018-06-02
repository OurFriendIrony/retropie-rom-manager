# Scripts to support retropie    
  
| **Build** | **Coverage** |
|---|---|
| [![Build Status](https://travis-ci.org/OurFriendIrony/python-retropie.png)](https://travis-ci.org/OurFriendIrony/python-retropie) | [![codecov](https://codecov.io/gh/OurFriendIrony/python-retropie/branch/master/graph/badge.svg)](https://codecov.io/gh/OurFriendIrony/python-retropie) |
  
## Prereqs  
`pip install -r requirements.txt`  
  
## Executing Tests  
`coverage run -m pytest -v`  
  
## Scripts  
**bgm**  
Provides background music to emulationstation  

**monitor_processes**  
Outputs entries when processes start and stop  
Mainly used to debug bgm.py  

**gpio_shutdown**  
When gpio input received, perform system shutdown  

**gpio_led_continuous**  
GPIO output to cycle led colours, continuously  

**gpio_led_pwm**  
GPIO output to cycle led colours, pwm  

**gpio_led_solid**  
GPIO output to cycle led colours, solid  
