'''
  This script turns on and off the allsky heater (a circular resistence)
  >> python Heater.py on
  >> python Heater.py off

'''

import RPi.GPIO as GPIO
import time, sys

from allsky.config import HEATER_PIN, HEATER_LOG

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(HEATER_PIN, GPIO.OUT)

class Heater:
  def __init__(self, do=1):
    self.logname = HEATER_LOG
    self.On() if do else self.Off()

  def On(self):
    GPIO.output(HEATER_PIN, GPIO.HIGH)
    self.WriteLog(1)

  def Off(self):
    GPIO.output(HEATER_PIN, GPIO.LOW)
    self.WriteLog(0)

  def WriteLog(self, ison=0):
    with open(self.logname, 'w') as f:
      f.write("%1.0f"%int(ison))

  def ReadLog(self):
    with open(self.logname, 'r') as f:
      r = f.read()
    r = r.replace('\n', '').replace(' ', '')
    try:
      return int(r)
    except:
      return 0

if __name__ == '__main__':
  h = Heater()
  h.Off()

  if len(sys.argv) == 1:
    print('Testing heater -- turning ON and OFF')
    while(1):
      h.On()
      time.sleep(1)
      h.Off()
      time.sleep(1)

  elif len(sys.argv) >= 2:
    arg = sys.argv[-1]
    if arg.lower() == 'on':
      print('CCD heater -- ON')
      h.On()
      time.sleep(1)
    else:
      print('CCD heater -- OFF')
      h.Off()
      time.sleep(1)
    exit()

