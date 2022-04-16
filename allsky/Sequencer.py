from allsky.ServoControler import ServoControl
from allsky.run import *
from allsky.config import TIME_INTERVAL_NIGHT, TIME_INTERVAL_DAY

from allsky.zwo import zwo
import allsky.obscoor

import time, random, os, sys

SC = ServoControl()
cam = zwo()
cam.SetOutName('pic')
doDarks = False

while True:
  if Allsky_IsOff(): 
    print("Finishing...")
    SC.CloseDome()
    time.sleep(2)
    break

  isNight = cam.coor.IsNight()
  if not doDarks: SC.OpenDome()
  else: SC.CloseDome()
  time.sleep(2)
  cam.SetSufixTimeNow()
  cam.prefix = None

  if not isNight: 
    cam.GetAutoExposure(fixGain=0)
    time.sleep(2)
    cam.SnapFIT()
    time.sleep(2)
    cam.SnapJPEG()
    time.sleep(TIME_INTERVAL_DAY )
    if cam.verbose: print('Waiting %i minutes...'%(TIME_INTERVAL_DAY/60))
  else:
    if not doDarks:
      cam.GetAutoExposure()
      time.sleep(2)
      cam.SnapFIT()
      time.sleep(2)
      cam.SnapJPEG()
      time.sleep(2)
      cam.GetAutoExposure(fixGain=0)
      time.sleep(2)
      cam.SetPrefix('gain0')
      cam.SnapFIT()
      if cam.verbose: print('Waiting %i minutes...'%(TIME_INTERVAL_NIGHT/60))
      time.sleep(TIME_INTERVAL_NIGHT)
    else:
      cam.SetSufix(None)
      temp = cam.GetTemperature()
      gain = random.choice([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
      texp = random.choice([500, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 12000, 15000])
      cam.SetPrefix('dark_%i_%i_%i'%(temp,gain,texp))
      fname = cam.GetOutPath()
      if not os.path.isfile(fname): 
        cam.SetExposure(texp*1000)
        cam.SetGain(gain)
        cam.SnapFIT()
      time.sleep(120)

