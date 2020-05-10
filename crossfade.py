import os
import gpiozero
import pygame
import math
import time

# Allows PyGame to run headless
os.putenv('SDL_VIDEODRIVER', 'dummy')

# Channel selection rotary encoder
rotary_clk = gpiozero.DigitalInputDevice(23)
rotary_dt = gpiozero.DigitalInputDevice(24)
rotary_clk_last_value = rotary_clk.value
rotary_dt_last_value = rotary_dt.value
rotary_last_position = 0
rotary_position = 0
rotary_last_change_time = int(time.time())

# Decalre our 'stations'
station_files = [
  'audio/1.wav',
  'audio/2.wav',
  'audio/airplay.wav'
]

# 'System' audio files
static_file = 'audio/static.wav'

# Initialise everything
pygame.init()
pygame.mixer.init()

# Start static playback
static_sound = pygame.mixer.Sound(static_file)
static_channel = pygame.mixer.Sound.play(static_sound, loops=-1)

# Start station playback
stations = []
for station_file in station_files:
  station_sound = pygame.mixer.Sound(station_file)
  stations.append(pygame.mixer.Sound.play(station_sound, loops=-1))

# Special stations
specials = {
  2: "airplay"
}

special = {
 station: "",
 selected = False,
 active = False
}

# Set initial volume levels
static_channel.set_volume(1)
stations[0].set_volume(0)
stations[1].set_volume(0)
stations[2].set_volume(0)

def setTuning():
  global rotary_position, stations, static_channel, specials, special
  
  channel = math.floor(rotary_position / 10) # Each channel or phase is based on a range of 10 positions
  channel_position = (rotary_position % 10) / 10 # The position within each channel can be used to set the correct mix levels
  station = math.floor(channel / 4) # Which station are we dealing with?
  fading = channel % 2 == 0 # Are we in a fade state?
  fading_in = channel % 4 == 0 # Are we fading in to a station or away from it
  static = (channel + 1) % 4 == 0 # Should we just play static?

  print("Position: %s, Channel: %s, Channel Position: %s, Station: %s, Fading: %s, Fading In: %s, Static: %s" % (rotary_position, channel, channel_position, station, fading, fading_in, static))

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
    special.station = specials[station]
    special.selected = True
    special.active = False

while True:
    
    rotary_clk_value = rotary_clk.value
    rotary_dt_value = rotary_dt.value
    
    # If in a change state, work out which direction
    if rotary_clk_value == 0 and rotary_dt_value == 1:
      if rotary_clk_last_value == 1 and rotary_dt_last_value == 1:
        rotary_position += 1
        if rotary_position >= len(stations) * 40:
          rotary_position = 0 
      elif rotary_clk_last_value == 0 and rotary_dt_last_value == 0:
        rotary_position -= 1
        if rotary_position <= -1:
          rotary_position += len(stations) * 40

      rotary_last_position = rotary_position
      rotary_last_change_time = int(time.time())

      if special.active:
        print('Deactivating %s' % special.station)
        special.station = ""
        special.selected = False
        special.active = False
        rotary_position = 0
        rotary_last_position = 0
        pygame.mixer.start()

      setTuning()

    rotary_clk_last_value = rotary_clk_value
    rotary_dt_last_value = rotary_dt_value

    # When you've been set on a special station for over 5 seconds, activate
    if special.selected and not special.active and int(time.time()) - rotary_last_change_time > 5:
      print('Activating %s' % special.station)
      # Stop all playback
      pygame.mixer.stop()
      # Call sync service
      special.active = True

    time.sleep(0.01)

