from allsky.ServoControler import ServoControl
from allsky.run import *
from allsky.config import TIME_INTERVAL_NIGHT, TIME_INTERVAL_DAY

from allsky.zwo import zwo
import allsky.obscoor

import time

SC = ServoControl()
cam = zwo()
cam.SetOutName('pic')

while True:
  if Allsky_IsOff(): 
    print("Finishing...")
    SC.CloseDome()
    time.sleep(2)
    break

  isNight = cam.coor.IsNight()
  SC.OpenDome()
  time.sleep(2)
  cam.SetSufixTimeNow()
  cam.prefix = None

  if not isNight: 
    cam.GetAutoExposure(gain=0)
    cam.GetAutoExposure()
    cam.SnapFIT()
    cam.SnapJPEG()
    time.sleep(TIME_INTERVAL_DAY )
    if cam.verbose: print('Waiting %i minutes...'%(TIME_INTERVAL_DAY/60))
  else:
    cam.GetAutoExposure()
    cam.SnapFIT()
    cam.SnapJPEG()
    cam.GetAutoExposure(fixGain=0)
    cam.SetPrefix('gain0')
    cam.SnapFIT()
    if cam.verbose: print('Waiting %i minutes...'%(TIME_INTERVAL_NIGHT/60))
    time.sleep(TIME_INTERVAL_NIGHT)

