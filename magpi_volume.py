import gpiozero
import os
from time import sleep

clk = gpiozero.DigitalInputDevice(23)
dt = gpiozero.DigitalInputDevice(24)
clk_last_value = clk.value
dt_last_value = dt.value
position = 0

# Set initial volume
# You may need to change Digital depending on your setup
os.system('amixer set Digital 0%')

while True:

    clk_value = clk.value
    dt_value = dt.value

    # If in a change state, work out which direction
    if clk_value == 0 and dt_value == 1:
        if clk_last_value == 1 and dt_last_value == 1 and position < 20:
            position += 1
        elif clk_last_value == 0 and dt_last_value == 0 and position > 0:
            position -= 1

        # We multiply by 5 to speed up the process. Try changing it.
        os.system('amixer set Digital ' + str(position * 5) + '%')

    clk_last_value = clk_value
    dt_last_value = dt_value

    sleep(0.001)
