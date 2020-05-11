import os
import gpiozero
import pygame
import math
import time
from rotary import RotaryEncoder
from station import Station

# Allows PyGame to run headless
os.putenv('SDL_VIDEODRIVER', 'dummy')

# Declare our 'stations'
stations = [
  Station('audio/1.ogg', 100),
  Station('audio/2.ogg', 100),
  Station('audio/airplay.wav', 3, True, "airplay")
]

# Initialise everything
pygame.init()
pygame.mixer.init()

# Prep static channel and annoucements
static_sound = pygame.mixer.Sound('audio/static.wav')
activating_sound = pygame.mixer.Sound('audio/activating.wav')
deactivating_sound = pygame.mixer.Sound('audio/deactivating.wav')

# Start static playback
static_channel = pygame.mixer.Sound.play(static_sound, loops=-1)
static_channel.set_volume(1)

# Start station playback
current_station = 0
stations[current_station].play(pygame)

# Set up controls
selector = RotaryEncoder(23, 24, len(stations) * 40)
selector_last_position = 0

def set_tuning(position):
  global stations, current_station, pygame
  
  channel = math.floor(position / 10) # Each channel or phase is based on a range of 10 positions
  channel_position = (position % 10) / 10 # The position within each channel can be used to set the correct mix levels
  station = math.floor(channel / 4) # Which station are we dealing with?
  fading = channel % 2 == 0 # Are we in a fade state?
  fading_in = channel % 4 == 0 # Are we fading in to a station or away from it
  static = (channel + 1) % 4 == 0 # Should we just play static?

  print("Position: %s, Channel: %s, Channel Position: %s, Station: %s, Fading: %s, Fading In: %s, Static: %s" % (position, channel, channel_position, station, fading, fading_in, static))

  # Swap out the channel during fade in/out
  if fading and current_station != station:
    stations[station].play(pygame)
    current_station = station
    print("Changed active station to %s" % current_station)
    
  # Set the volume levels
  if static:
    pygame.mixer.music.set_volume(0)
    static_channel.set_volume(1)
  elif not fading:
    pygame.mixer.music.set_volume(1)
    static_channel.set_volume(0)
  elif fading_in:
    pygame.mixer.music.set_volume(channel_position)
    static_channel.set_volume(1 - channel_position)
  else:
    pygame.mixer.music.set_volume(1 - channel_position)
    static_channel.set_volume(channel_position)

# Start monitoring the station selector rotary encoder
selector.watch()

while True:
    
    selector_position = selector.position
    if selector_position != selector_last_position:
      #  Shutdown a special service and reset everything
      if stations[current_station].special_active:
        print('Deactivating %s' % stations[current_station].name)
        stations[current_station].special_active = False
        selector_position = 0
        selector.position = 0
        selector.last_position = -1
        current_station = -1
        os.system('sudo service shairport-sync stop')
        pygame.mixer.init()
        pygame.mixer.Sound.play(deactivating_sound)
        time.sleep(1.5)
        static_channel = pygame.mixer.Sound.play(static_sound, loops=-1)
        
      set_tuning(selector_position)
      selector_last_position = selector.position
    
    # When you've been set on a special station for over 5 seconds, activate
    if stations[current_station].special and not stations[current_station].special_active and int(time.time()) - selector.last_change_time > 5:
      print('Activating %s' % stations[current_station].name)
      stations[current_station].special_active = True
      pygame.mixer.music.stop()
      pygame.mixer.Sound.play(activating_sound)
      time.sleep(1.5)
      os.system('sudo service shairport-sync start')
      pygame.mixer.quit()

    time.sleep(0.001)

