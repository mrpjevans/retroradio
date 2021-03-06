import os
from time import sleep
from rotary import RotaryEncoder

vol_control = RotaryEncoder(14, 15, min_val=0, max_val=20)
vol_control.watch()
vol_last_position = 10
vol_control.position = 10

# Set initial low volume
os.system('amixer set Digital 50%')

while True:
  if vol_control.position != vol_last_position:
    vol_last_position = vol_control.position
    os.system('amixer set Digital ' + str(vol_last_position * 5) + '%')
    print(vol_last_position * 5)
    
  sleep(0.001)
