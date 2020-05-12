import time

class Station:
  duration = 100
  file = ""
  launch_time = 0
  special = False
  special_active = False
  name = ""

  def __init__(self, file, duration, special=False, name=""):
    self.file = file
    self.duration = duration
    self.special = special
    self.name = name
    self.launch_time = int(time.time())

  def play(self, pygame):
    if pygame.mixer.music.get_busy():
      pygame.mixer.music.stop()
    pygame.mixer.music.load(self.file)
    pygame.mixer.music.set_volume(0)
    position = (int(time.time()) - self.launch_time) % self.duration
    pygame.mixer.music.play(loops=-1, start=position)


