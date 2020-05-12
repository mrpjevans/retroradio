import math

class PlaybackState:
  position = 0
  channel = 0
  channel_position = 0
  station = 0
  tuned = False
  fading = False
  fading_in = True
  fading_out = False
  static = False

  def calc_status(self, position):
    self.position = position
    self.channel = math.floor(self.position / 10) # Each channel or phase is based on a range of 10 positions
    self.channel_position = (position % 10) / 10 # The position within each channel can be used to set the correct mix levels
    self.station = math.floor(self.channel / 4) # Which station are we dealing with?
    self.fading = self.channel % 2 == 0 # Are we in a fade state?
    self.tuned = not self.fading # Are we tunded into a station
    self.fading_in = self.fading and self.channel % 4 == 0 # Are we fading in to a station or away from it
    self.fading_out = self.fading and not self.fading_in # If fading, is it in or out?
    self.static = (self.channel + 1) % 4 == 0 # Should we just play static?

  def print_status(self):
    print("Position: %s, Channel: %s, Channel Position: %s, Station: %s, Tuned: %s, Fading: %s, Fading In: %s, Fading Out: %s, Static: %s" % (self.position, self.channel, self.channel_position, self.station, self.tuned, self.fading, self.fading_in, self.fading_out, self.static))