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
station_files = [
  'audio/1.wav',
  'audio/2.wav',
  'audio/airplay.wav'
]

# Set up controls
selector = RotaryEncoder(23, 24, len(station_files) * 40)
selector_last_position = 0

# 'System' audio files
static_file = 'audio/static.wav'
activating_file = 'audio/activating.wav'
deactivating_file = 'audio/deactivating.wav'

# Initialise everything
pygame.init()
pygame.mixer.init()

# Prep static channel
static_sound = pygame.mixer.Sound(static_file)


# Prep announcements
activating_sound = pygame.mixer.Sound(activating_file)
deactivating_sound = pygame.mixer.Sound(deactivating_file)

# Start station playback
def start_playback():
  global static_channel, stations, station_files, static_sound
  static_channel = pygame.mixer.Sound.play(static_sound, loops=-1)
  static_channel.set_volume(1)
  stations = []
  for station_file in station_files:
    station_sound = pygame.mixer.Sound(station_file)
    station_channel = pygame.mixer.Sound.play(station_sound, loops=-1)
    station_channel.set_volume(0)
    stations.append(station_channel)

start_playback()

# Special stations for non-playback functionality
specials = {
  2: "airplay"
}

# Keep track of the current 'special' station
special = {
 "station": 0,
 "name": "",
 "selected": False,
 "active": False
}

def set_tuning(position):
  global stations, static_channel, specials, special
  
  channel = math.floor(position / 10) # Each channel or phase is based on a range of 10 positions
  channel_position = (position % 10) / 10 # The position within each channel can be used to set the correct mix levels
  station = math.floor(channel / 4) # Which station are we dealing with?
  fading = channel % 2 == 0 # Are we in a fade state?
  fading_in = channel % 4 == 0 # Are we fading in to a station or away from it
  static = (channel + 1) % 4 == 0 # Should we just play static?

  print("Position: %s, Channel: %s, Channel Position: %s, Station: %s, Fading: %s, Fading In: %s, Static: %s" % (position, channel, channel_position, station, fading, fading_in, static))

  if static:
    stations[station].set_volume(0)
    # This helps with underflow (when position is 0, it goes to 79)
    if station == len(stations) - 1:
      stations[0].set_volume(0)
    static_channel.set_volume(1)
  elif not fading:
    stations[station].set_volume(1)
    static_channel.set_volume(0)
  elif fading_in:
    stations[station].set_volume(channel_position)
    static_channel.set_volume(1 - channel_position)
  else:
    stations[station].set_volume(1 - channel_position)
    static_channel.set_volume(channel_position)
  
  if not static and not fading and station in specials.keys():
    special['station'] = station
    special['name'] = specials[station]
    special['selected'] = True
    special['active'] = False

selector.watch()

while True:
    
    selector_position = selector.position
    if selector_position != selector_last_position:
      #  Shutdown a special service and reset everything
      if special['active'] is True:
        print('Deactivating %s' % special['name'])
        selector_position = 0
        selector.position = 0
        selector.last_position = 0
        special['station'] = 0
        special['name'] = ""
        special['selected'] = False
        special['active'] = False
        os.system('sudo service shairport-sync stop')
        pygame.mixer.init()
        pygame.mixer.Sound.play(deactivating_sound)
        time.sleep(1.5)
        start_playback()
      
      set_tuning(selector_position)
      selector_last_position = selector.position
    
    # When you've been set on a special station for over 5 seconds, activate
    if special['selected'] and not special['active'] and int(time.time()) - selector.last_change_time > 5:
      print('Activating %s' % special['name'])
      special['active'] = True
      stations[special['station']].stop()
      pygame.mixer.Sound.play(activating_sound)
      time.sleep(1.5)
      os.system('sudo service shairport-sync start')
      pygame.mixer.quit()

    time.sleep(0.001)

