import os
import sys
import json
import pygame
import time
from rotary import RotaryEncoder
from station import Station
from playback_state import PlaybackState

# Allows PyGame to run headless
os.putenv('SDL_VIDEODRIVER', 'dummy')

dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

# Load the playlist (you can specify a playlist object on the command line)
playlist_file = sys.argv[1] if len(sys.argv) > 1 else dir_path + "/playlist.json"
with open(playlist_file) as json_file:
    playlist = json.load(json_file)

# Declare our 'stations'
stations = []
for playlist_item in playlist:
  stations.append(Station(playlist_item))

# Initialise everything
pygame.init()
pygame.mixer.init()

# Prep static channel and annoucements
static_sound = pygame.mixer.Sound(dir_path + '/audio/static.ogg')
activating_sound = pygame.mixer.Sound(dir_path + '/audio/activating.ogg')
deactivated_sound = pygame.mixer.Sound(dir_path + '/audio/deactivated.ogg')

# Start static playback
static_channel = pygame.mixer.Sound.play(static_sound, loops=-1)
static_channel.set_volume(1)

# A simple object to track playback state
state = PlaybackState()

# Start station playback
stations[state.station].play(pygame)

# Set up controls
selector = RotaryEncoder(23, 24, len(stations) * 40)
selector_last_position = 0

def set_tuning(position):
  global stations, state, pygame
  
  current_station = state.station

  state.calc_status(position)
  state.print_status()

  # Swap out the channel during fade in/out
  if current_station != state.station:
    stations[state.station].play(pygame)
    print("Changed active station to %s" % state.station)
    
  # Set the volume levels
  if state.static:
    pygame.mixer.music.set_volume(0)
    static_channel.set_volume(1)
  elif state.tuned:
    pygame.mixer.music.set_volume(1)
    static_channel.set_volume(0)
  elif state.fading_in:
    pygame.mixer.music.set_volume(state.channel_position)
    static_channel.set_volume(1 - state.channel_position)
  else: # Fading out
    pygame.mixer.music.set_volume(1 - state.channel_position)
    static_channel.set_volume(state.channel_position)

# Start monitoring the station selector rotary encoder
selector.watch()

while True:
    
    if selector.position != selector_last_position:
      #  Shutdown a special service and reset everything
      if stations[state.station].special_active:
        print('Deactivating %s' % stations[state.station].name)
        stations[state.station].special_active = False
                
        # Stop the special service
        if stations[state.station].name == 'airplay':
          os.system('sudo service shairport-sync stop')

        # Annouce deactivation then restart static channel
        pygame.mixer.init()
        pygame.mixer.Sound.play(deactivated_sound)
        time.sleep(1.5)
        static_channel = pygame.mixer.Sound.play(static_sound, loops=-1)

        # Reset the tuning position
        selector.position = 0
        selector.last_position = -1
        state.station = -1
        
      set_tuning(selector.position)
      selector_last_position = selector.position
    
    # When you've been set on a special station for over 5 seconds, activate
    elif state.tuned and stations[state.station].special and not stations[state.station].special_active and int(time.time()) - selector.last_change_time > 5:

      # Announce chnage to special service
      print('Activating %s' % stations[state.station].name)
      stations[state.station].special_active = True
      pygame.mixer.music.stop()
      pygame.mixer.Sound.play(activating_sound)
      time.sleep(1.5)

      # Release resources
      pygame.mixer.quit()

      # Start the special service
      if stations[state.station].name == 'airplay':
        os.system('sudo service shairport-sync start')
      elif stations[state.station].name == 'shutdown':
        os.system('sudo shutdown -h now')
      
    time.sleep(0.001)

