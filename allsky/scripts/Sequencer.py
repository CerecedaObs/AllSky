from allsky.config import TIME_INTERVAL_NIGHT, TIME_INTERVAL_DAY, OUTPUT_IMAGES_DIR

from allsky.zwo import zwo
import time, os

# TODO: por la noche, sacar solo FITs... luego corregir y transformar los FITs en jpgs y borrar los originales (excepto por aquellos de gain=0, cada 2min)

def SetOutPathToday(cam=None):
  outpathbase = OUTPUT_IMAGES_DIR
  # folder with date for today, e.g. 2019-01-20 (10th January 2019)
  local_time = time.localtime(time.time())
  daytime = time.localtime(time.time()-12*3600)
  daytimestr = time.strftime('%Y-%m-%d', daytime)
  outpath = os.path.join(outpathbase, daytimestr)
  if not os.path.exists(outpath):
    os.makedirs(outpath)
  print('Output path: ', outpath)
  if cam is not None: cam.SetOutPath(outpath)
  return outpath

cam = zwo(verbose=1)
SetOutPathToday(cam)
cam.SetOutName('pic')

# Initialize with auto exp based on time of the day
cam.Auto(target=120, tolerance=50, fix=True, log=True, startFrom='time')

t0 = time.time()
while True:
  dt = time.time() - t0
  SetOutPathToday(cam)
  cam.SetSufixTimeNow()
  cam.SetPrefix(None)

  # Day time :   > pic each 30 seconds,  gain = 0, 
  if (not cam.coor.IsNight()) and (not cam.coor.IsDayButCloseToSunsetSunrise()):
    if cam.verbose: print('Day time! Taking picture...')
    if dt > 120: cam.Auto(forcegain=0, method='max', frac_saturated=0.07, fix=True, log=True)
    cam.Snap(format='jpeg', auto=True, recalculate_each_min=None)

  # Civil twilight or day close to sunset/sunrise, pic each 30 seconds, gain = 0,  recalculate every time
  elif (not cam.coor.IsNight()) and (cam.coor.IsDayButCloseToSunsetSunrise()):
    if cam.verbose: print('Day time - less than 1h from sunrise or sunset! Taking picture...')
    cam.Auto(forcegain=0, method='max', frac_saturated=0.07, fix=True, log=True)
    cam.Snap(format='jpeg', auto=True, recalculate_each_min=None)

  # Nautical twilight, pic each 30 seconds, gain = 20, Recalculate every time
  elif cam.coor.IsNight() and not cam.coor.IsAstronomicalTwilight():
    if cam.verbose: print('Night time - civil/nautical twilight! Taking picture...')
    cam.Auto(forcegain=40, method='max', frac_saturated=0.07, fix=True, log=True, target=120, tolerance=50)
    cam.Snap(format='jpeg', auto=True, recalculate_each_min=None)
    if cam.GetExposureTime() > 1: # we need to get a .fit and apply a dark substraction
      time.sleep(cam.GetExposureTime()/2)
      cam.Snap(format='fit', auto=True, recalculate_each_min=None)

  elif cam.coor.IsAstronomicalTwilight():
    if cam.verbose: print('Night time - astronomical twilight! Taking picture...')
    cam.Auto(forcegain=60, method='max', frac_saturated=0.07, fix=True, log=True, target=90, tolerance=60)
    cam.Snap(format='jpeg', auto=True, recalculate_each_min=None)
    if cam.GetExposureTime() > 1 and False: # we need to get a .fit and apply a dark substraction
      time.sleep(cam.GetExposureTime()/2)
      cam.Snap(format='fit', auto=True, recalculate_each_min=None)

  else:
    print('WARNING: Unknown time!')
    print('Is night = ', cam.coor.IsNight())
    print('Is day but close to sunset/sunrise = ', cam.coor.IsDayButCloseToSunsetSunrise())
    print('Is nautical twilight = ', cam.coor.IsNauticalTwilight())
    print('Is astronomical twilight = ', cam.coor.IsAstronomicalTwilight())

  outname = cam.GetFileName('jpg')
  lastpath = '/home/astroberry/AllSky/last.jpg'
  # copy
  os.system('cp %s %s'%(outname, lastpath))

  # every 2 minutes, recalculate using max salurated pixels and take FITs
  if dt >= 120:
    if cam.verbose: print('Taking FITs... after %1.2fs!'%(cam.GetExposureTime()/2))
    prevExp = cam.GetExposure() # in sec e-6
    prevGain = cam.GetGain()
    time.sleep(cam.GetExposureTime()/2)
    cam.SetPrefix('gain0')
    cam.Auto(forcegain=0, method='max', frac_saturated=0.04, fix=True, log=True, tolerance=50)
    cam.Snap(format='fit', auto=True, recalculate_each_min=None)
    time.sleep(cam.GetExposureTime()/2)
    t0 = time.time()
    cam.SetExposure(prevExp)
    cam.SetGain(prevGain)
    cam.WriteLog()

  interval = TIME_INTERVAL_NIGHT if cam.coor.IsNight() else TIME_INTERVAL_DAY
  if cam.verbose: print('Waiting %i seconds...'%interval)
  time.sleep(interval)


