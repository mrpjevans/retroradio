import gpiozero
import time
import threading

class RotaryEncoder:

  clk = None
  dt = None
  clk_last_value = 0
  dt_last_value = 0
  position = 0
  last_position = 0
  last_change_time = 0
  overflow = 100
  min_val = 0
  max_val = 0

  def __init__(self, clk_pin, dt_pin, overflow=None, min_val=None, max_val=None):
    self.clk = gpiozero.DigitalInputDevice(clk_pin)
    self.dt = gpiozero.DigitalInputDevice(dt_pin)
    self.clk_last_value = self.clk.value
    self.dt_last_value = self.dt.value
    self.position = 0
    self.last_position = 0
    self.last_change_time = int(time.time())
    self.overflow = overflow
    self.min_val = min_val
    self.max_val = max_val
  
  def watch(self):
    x = threading.Thread(target=self.__read_encoder, daemon=True)
    x.start()

  def __read_encoder(self):

    while True:
        
      clk_value = self.clk.value
      dt_value = self.dt.value
      
      # If in a change state, work out which direction
      if clk_value == 0 and dt_value == 1:
        if self.clk_last_value == 1 and self.dt_last_value == 1:
          self.position += 1
          if self.overflow and self.position >= self.overflow:
            self.position = 0 
        elif self.clk_last_value == 0 and self.dt_last_value == 0:
          self.position -= 1
          if self.overflow and self.position <= -1:
            self.position += self.overflow

        if self.min_val is not None and self.position < self.min_val:
          self.position = self.min_val
        if self.max_val is not None and self.position > self.max_val:
          self.position = self.max_val

        self.last_position = self.position
        self.last_change_time = int(time.time())
      
      self.clk_last_value = clk_value
      self.dt_last_value = dt_value
      
      time.sleep(0.001)
