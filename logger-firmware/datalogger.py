import pyb
from util import *
import utime

#how delay between data captures in milliseconds
DELAY_BETWEEN_CYCLES = 15 * 1000
#frequency of data capture in a frame in Hz
FREQ = 10
#capture frame duration in milliseconds
DURATION = 1000
_in_frame_delay = 1000 // FREQ
_n = DURATION // _in_frame_delay
accel = pyb.Accel()
switch = pyb.Switch()
rtc = pyb.RTC()
# rtc.wakeup(DELAY_BETWEEN_CYCLES)
datetime = rtc.datetime()
filename = "/sd/log.{}-{:0>2}-{:0>2}.csv".format(datetime[0], datetime[1], datetime[2])

def log_series():
    with open(filename, 'a+') as log:
        for i in range(0, _n):
            t = utime.time()
            x, y, z = accel.filtered_xyz()
            log.write('{},{},{},{}\n'.format(t, x, y, z))
            # blink_led(orange, 2, 20)
            pyb.delay(_in_frame_delay)
        # for i in range(1, _n):
        #     x, y, z = accel.filtered_xyz()
        #     log.write(',{},{},{}\n'.format(x, y, z))
while True:
    log_series()
    blink_led(orange, 2, 20)
    if switch():
        blink_led(blue)
        break
    pyb.delay(500)
    # pyb.stop()