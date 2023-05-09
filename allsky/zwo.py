#!/usr/bin/env python

import argparse
import os, sys, time, json
import zwoasi as asi
from astropy.io import fits
import cv2
import numpy as np

from allsky.obscoor import obscoor
from allsky.config import SDK_LIB_PATH, OUTPUT_IMAGES_DIR, ZWO_LOG, ZWO_EXPMAX


class zwo:

  def __init__(self, verbose=1):
    # Init
    asi.init(SDK_LIB_PATH)

    # Look for a camera and connect
    cameras_found = asi.list_cameras()  # Models names of the connected cameras
    self.verbose = verbose
    if len(cameras_found) == 0:
      print('No camera found!')
      exit()
    if self.verbose: print("Using: %s"%cameras_found[0])

    self.camera = asi.Camera(0)
    self.name = cameras_found[0]
    self.camera_info = self.camera.get_camera_property()
    self.controls = self.camera.get_controls()
    self.SetDefaultValues()
    self.filename = 'temp'
    self.outpath = './'
    self.prefix = None
    self.sufix = None
    self.coor = obscoor()
    self.SetOutPath(OUTPUT_IMAGES_DIR)


  #######################################################################################################################
  ### Save and read logs
  #######################################################################################################################

  def CraftFitsHeader(self):
    ''' Craft fits header '''
    # Temperature, exposure time, gain
    # type (dark, light), date, humidity, site coordinates
    settings = self.camera.get_control_values()
    headerdic = {}
    headerdic['GAIN']= settings['Gain']
    headerdic['EXPTIME'] = float(settings['Exposure'])/1e6
    headerdic['CCDTEMP'] = float(settings['Temperature'])/10 
    headerdic['AUTHOR'] = "CERECEDA OBS" 
    headerdic['INSTRUME'] = self.name 
    headerdic['TELESCOP'] = "ALLSKY"
    headerdic['DATE'] = self.coor.GetTimeNow()
    return headerdic

  def WriteLog(self):
    ''' Log the current settings '''
    header = self.CraftFitsHeader()
    with open(ZWO_LOG, 'w') as f:
      json.dump(header, f, indent=2)
    return
  
  def ReadLog(self):
    ''' Read the log '''
    with open(ZWO_LOG, 'r') as f:
      header = json.load(f)
    return header
    
  def SettingFromLog(self, set=True):
    ''' Set the camera settings from the log '''
    log = self.ReadLog()
    gain = int(log['GAIN'])
    exptime = int(float(log['EXPTIME'])*1e6)
    if set:
      self.SetGain(gain)
      self.SetExposure(exptime)
    return gain, exptime


  #######################################################################################################################
  ### Set methods
  #######################################################################################################################

  def SetOutName(self, name):
    ''' Set out name '''
    self.filename = name

  def SetOutPath(self, name):
    ''' Set out path '''
    self.outpath = name

  def SetExposure(self, exposure):
    ''' Set exposure '''
    if self.verbose >= 2: print('Setting exposure to %i'%int(exposure))
    self.camera.set_control_value(asi.ASI_EXPOSURE, exposure)

  def SetGain(self, gain):
    ''' Set gain '''
    if self.verbose >= 2: print('Setting gain to %i'%(int(gain)))
    self.camera.set_control_value(asi.ASI_GAIN, gain)

  def SetDefaultValues(self):
    ''' Set to MY default values '''
    #self.camera.set_control_value(asi.ASI_BANDWIDTHOVERLOAD, camera.get_controls()['BandWidth']['MinValue']) # Use minimum USB bandwidth permitted
    #self.camera.disable_dark_subtract()
    self.camera.set_control_value(asi.ASI_GAIN, 10)
    self.camera.set_control_value(asi.ASI_EXPOSURE, 1000000)
    self.camera.set_control_value(asi.ASI_WB_B, 99)
    self.camera.set_control_value(asi.ASI_WB_R, 75)
    self.camera.set_control_value(asi.ASI_GAMMA, 50)
    self.camera.set_control_value(asi.ASI_BRIGHTNESS, 50)
    self.camera.set_control_value(asi.ASI_FLIP, 0)

  def RestoreDefaultControls(self):
    ''' Restore all controls to zwo-default values except USB bandwidth '''
    for c in self.controls:
      if self.controls[c]['ControlType'] == asi.ASI_BANDWIDTHOVERLOAD:
        continue
      self.camera.set_control_value(self.controls[c]['ControlType'], self.controls[c]['DefaultValue'])

  def SetTimeOut(self):
    ''' Set the timeout '''
    timeout = (self.camera.get_control_value(asi.ASI_EXPOSURE)[0] / 1000) * 2 + 500
    self.camera.default_timeout = timeout


  #######################################################################################################################
  ### Get methods
  #######################################################################################################################

  def SetPrefix(self, pr):
    self.prefix = pr

  def SetSufix(self, sf):
    self.sufix = sf

  def SetSufixTimeNow(self):
    sufix = self.coor.GetTimeNow("%Y_%m_%d_%H_%M_%S")
    self.SetSufix(sufix)

  def GetTemperature(self):
    settings = self.camera.get_control_values()
    return settings['Temperature']

  def GetOutName(self):
    ''' Craft the name of the output file, considering the prefix and sufix, if any '''
    name = self.prefix + '_' if self.prefix is not None else ''
    name += self.filename
    name += '_'+self.sufix if self.sufix is not None else ''
    return name

  def GetOutPath(self):
    ''' Get the output path and creates the directory if does not exist '''
    if not self.outpath.endswith('/'): self.outpath += '/'
    if not os.path.isdir(self.outpath):
      os.system('mkdir -p %s'%self.outpath)
      if self.verbose >= 2: print("Created output directory: ", self.outpath)
    return self.outpath

  def GetFileName(self, format='jpg', name=None):
    ''' Crafts the output file name for a given format '''
    while format.startswith('.'): format = format[1:]
    outname = self.GetOutName() if name is None else name
    if outname.lower().endswith('.' + format.lower()):
      filename = self.GetOutPath() + outname
    else:
      filename = self.GetOutPath() + outname + '.' + format
    return filename


  def GetExposure(self):
    ''' Get exposure '''
    return self.camera.get_control_value(asi.ASI_EXPOSURE)[0]

  def GetExposureTime(self):
    ''' Get exposure time in seconds '''
    return self.camera.get_control_value(asi.ASI_EXPOSURE)[0]/1e6
  
  def GetGain(self):
    ''' Get gain '''
    return self.camera.get_control_value(asi.ASI_GAIN)[0]

  #######################################################################################################################
  ### Prints and verbosity
  #######################################################################################################################

  def PrintCameraControls(self):
    ''' Print camera controls '''
    print('Camera controls:')
    controls = self.camera.get_controls()
    for cn in sorted(controls.keys()):
        print('    %s:' % cn)
        for k in sorted(controls[cn].keys()):
          print('        %s: %s' % (k, repr(controls[cn][k])))

  def PrintControlValues(self):
    ''' Print camera control values '''
    print('Camera control values:')
    settings = self.camera.get_control_values()
    for k in sorted(settings.keys()):
      print('  > %s: %s' % (k, str(settings[k])))


  #######################################################################################################################
  ### Snap
  #######################################################################################################################

  def PrepareVideo(self):
    # Enable video mode
    try:
      # Force any single exposure to be halted
      self.camera.stop_exposure()
    except (KeyboardInterrupt, SystemExit):
      raise
    except:
      pass

  def SnapTIFF(self, outname=None, verbose=None):
    ''' Save a monocolor 16-bit tiff image '''
    if verbose is None: verbose = self.verbose
    if verbose: print('Capturing a single 16-bit mono with exp = %gs and gain = %1.0f'%(self.camera.get_control_value(asi.ASI_EXPOSURE)[0]/1e6, self.camera.get_control_value(asi.ASI_GAIN)[0]))
    filename = self.GetFileName('tiff')
    self.camera.set_image_type(asi.ASI_IMG_RAW16)
    self.camera.capture(filename=filename)
    if verbose: print('Saved to %s' % filename)

  def SnapJPEG(self, outname=None, verbose=None):
    ''' Save color jpeg image '''
    filename = self.GetFileName('jpg', outname)
    self.camera.set_image_type(asi.ASI_IMG_RGB24)
    if verbose is None: verbose = self.verbose
    if verbose: print('Capturing a single, color image with exp = %gs and gain = %1.0f'%(self.camera.get_control_value(asi.ASI_EXPOSURE)[0]/1e6, self.camera.get_control_value(asi.ASI_GAIN)[0]))
    self.camera.capture(filename=filename)
    if verbose: print('Saved to %s' % filename)

  def SnapFIT(self, outname=None, verbose=None):
    ''' Save a FITs file '''
    self.camera.set_image_type(asi.ASI_IMG_RAW16)
    if verbose is None: verbose = self.verbose
    if verbose: print('Capturing a single 16-bit FITS with exp = %gs and gain = %1.0f'%(self.camera.get_control_value(asi.ASI_EXPOSURE)[0]/1e6, self.camera.get_control_value(asi.ASI_GAIN)[0]))
    img = self.GetRawImage()
    hdu = fits.PrimaryHDU(img)
    filename = self.GetFileName('fit', outname)
    header = self.CraftFitsHeader()
    for k in header: hdu.header[k] = header[k]
    if os.path.isfile(filename): os.system('mv %s %s.old'%(filename, filename))
    hdu.writeto(filename)
    if verbose: print('Saved to %s' % filename)

  def Snap(self, format='jpg', auto=True, recalculate_each_min=10, outname=None, verbose=None):
    ''' Snap a single image '''
    if recalculate_each_min is not None and recalculate_each_min >= 0:
      log = self.ReadLog()
      prev = log['DATE']
      now = self.coor.GetTimeNow()
      if (now - prev).total_seconds() > recalculate_each_min * 60:
        exposure, gain = self.AutoExposure()
        self.SetGain(gain)
        self.SetExposure(exposure)
    elif auto:
      self.SettingFromLog()
    ## Snap -- use functions depending on the format
    if format.lower() == 'tiff':
      self.SnapTIFF(outname=outname)
    elif format.lower() == 'jpg' or format.lower() == 'jpeg':
      self.SnapJPEG(outname=outname)
    elif format.lower() == 'fit' or format.lower() == 'fits':
      self.SnapFIT(outname=outname)
    self.WriteLog()
    #if self.verbose >= 1:
    #  self.PrintControlValues()

  def VideoSnap(self):  
    if self.verbose: print('Enabling video mode')
    self.PrepareVideo()
    self.camera.start_video_capture()
    self.sufix = 'video'
    filename = self.GetFileName('jpg')
    self.camera.set_image_type(asi.ASI_IMG_RGB24)
    self.camera.capture_video_frame(filename=filename)
    if self.verbose: print('Saved to %s' % filename)

  def GetRawImage(self):
    ''' Get a numpy image '''
    return self.camera.capture()

  def SaveControlValues(self):
    ''' Save the control values in a txt file '''
    self.sufix = 'settings'
    filename = self.GetFileName('txt')
    settings = self.camera.get_control_values()
    with open(filename, 'w') as f:
        for k in sorted(settings.keys()):
            f.write('%s: %s\n' % (k, str(settings[k])))
    if self.verbose: print('Camera settings saved to %s' % filename)


  #######################################################################################################################
  ### Auto exposure
  #######################################################################################################################

  def GetAutoGain(self):
    ''' Get gain based on day status '''
    if not self.coor.IsNight():
      return 0
    elif not self.coor.IsAstronomicalTwilight():
      return 40
    else:
      return 60

  def GetAutoExposure(self):
    ''' Get exposure based on day status '''
    if not self.coor.IsNight():
      return int(0.05e6) # 50 ms for day time
    elif not self.coor.IsNauticalTwilight():
      return int(0.51e6) # 0.5s for civil twilight
    elif not self.coor.IsAstronomicalTwilight():
      return int(1.01e6) # 1s for nautical twilight
    else:
      return int(4.0e6) # 4s for astronomical twilight

  def GetAutoFromCurrentTime(self, set=True):
    ''' Set gain and exp time based on the current time '''
    gain = self.GetAutoGain()
    exp = self.GetAutoExposure()
    if set:
      self.SetGain(gain)
      self.SetExposure(exp)
    return gain, exp

  def AutoExposure(self, initial_exposure=None, tolerance=20, target=150, max_iterations=10, gain=None, frac_saturated=None, method='average'):
    ''' Get autoexposure by hand 
        Method: average
          Take average pixel value and take it to [target] with a tolerance of [tolerance], ignore saturated pixels
        Method: median
          Take median pixel value and take it to [target] with a tolerance of [tolerance], ignore saturated pixels
        Method: max
          Take the number of saturated pixels to be less than [frac_saturated] *or* median to target with some tolerance
    '''
    if gain is None: 
      gain = self.GetAutoGain()
    elif gain < 0: # take the previous value
      gain, exp = self.SettingFromLog(set=False)
    if initial_exposure is None:
      _, initial_exposure = self.SettingFromLog(set=False)
      
    self.SetGain(gain)
    exposure = initial_exposure
    iteration = -1

    ofname = self.GetFileName('jpg', 'for_auto_exp')
    reachedMValue = False

    while iteration < max_iterations:
        # Take a picture with the current gain and exposure settings
        iteration += 1
        self.SetExposure(exposure)
        self.SnapJPEG(outname='for_auto_exp', verbose=False)

        # Read the output image and calculate the mean pixel value
        image = cv2.imread(ofname)

        if method == 'average' or method == 'max':
          value = np.mean(image)
        elif method == 'median':
          value = np.median(image)

        n_satruated = np.sum(image == 255)
        n_total = np.sum(np.ones(image.shape))
        frac = n_satruated / n_total

        # Check if the mean pixel value is within the tolerance range of the target mean
        if float(target - tolerance) <= value <= float(target + tolerance) or reachedMValue:
          reachedMValue = True
          if method == 'max' and frac > frac_saturated:
            exposure = int(exposure*0.8)
            if self.verbose >= 2:
              print('Saturated = ', frac*100, '%. Reducing exposure to ', exposure)
            continue

          if self.verbose:
            print(f"Auto exposure successful. Gain: {gain}, Exposure: {exposure}, Frac of saturated pexels: {frac*100:.2f}%")
          self.SetExposure(exposure)
          return exposure

        # Adjust the exposure based on the mean pixel value
        # gain = min(gain * ratio , 100)  # Assuming the maximum gain value is 255
        ratio = target / value
        if self.verbose >= 2:
          print('value = ', value, ', target = ', target, ', tolerance = ', tolerance, ', ratio = ', ratio, ', exposure = ', exposure)
        exposure = int(exposure * ratio)

        # Wait a bit so the camera rests... this avoid some errors from the camera
        time.sleep(exposure/1e6/2)

        if exposure > ZWO_EXPMAX*1e6:
          print('Setting exposure to max: ', ZWO_EXPMAX, 's')
          exposure = int(ZWO_EXPMAX*1e6)
          self.SetExposure(exposure)
          return exposure

    print("Auto exposure failed to converge. Using the previous settings.")
    self.SetExposure(exposure)
    return exposure

  def Auto(self, forcegain=None, target=150, tolerance=20, frac_saturated=0.07, method='average', fix=True, log=True, startFrom='log', verbose=1):
    ''' Check if auto exposure and auto gain is giving good results -- if not, set it automatically '''
    if startFrom.lower().startswith('log'):
      # Based on previous logs
      gain, exposure = self.SettingFromLog(set=False)
    else:
      # Based on current day/night time
      gain, exposure = self.GetAutoFromCurrentTime(set=False)
    if forcegain is not None:
      gain = forcegain
    self.SetGain(gain)
    self.SetExposure(exposure)
    self.SnapJPEG(outname='for_auto_exp')
    ofname = self.GetFileName('jpg', 'for_auto_exp')
    image = cv2.imread(ofname)
    value = np.mean(image) if method.lower() != 'median' else np.median(image)
    if method.lower() == 'max':
      n_satruated = np.sum(image == 255)
      n_total = image.shape[0] * image.shape[1]
      frac = n_satruated / n_total
      if frac > frac_saturated:
        print(f'Check failed: {frac*100:.2f}% of the pixels are saturated')
        if fix:
          print('Running auto exposure... (after waiting %1.2f s)'%(exposure/2))
          time.sleep(exposure/1e6/2)
          self.AutoExposure(target=target, tolerance=tolerance, initial_exposure=exposure, gain=gain, frac_saturated=frac_saturated, method=method)
          if log: self.WriteLog()
        return False
    if not ((target - tolerance) <= value <= (target+tolerance)):
      print(f'Check failed: mean/median value is {value:.2f} (target: {target:.2f} +- {tolerance:.2f})   (method is {method})')
      if fix:
        print('Running auto exposure... (after waiting %1.2f s)'%(exposure/2))
        time.sleep(exposure/1e6/2)
        self.AutoExposure(target=target, tolerance=tolerance, initial_exposure=exposure, gain=gain, frac_saturated=frac_saturated, method=method)
        if log: self.WriteLog()
      return False
    if log: self.WriteLog()
    time.sleep(exposure/1e6/2)
    return True
    


####################################################################################################################
#### Main function... call this script to take a pic
####################################################################################################################

def main():
  parser = argparse.ArgumentParser(description='Take a pic')
  parser.add_argument('--exposure', '-t',  default=None, help='Exposure time')
  parser.add_argument('--gain', '-g',  default=None, help='Gain')
  parser.add_argument('--format', '-f',  default='', help='Output format: TIFF, fits, jpg...')
  parser.add_argument('--name', '-o',  default='temp', help='Output name')
  parser.add_argument('--verbose', '-v', default=1, help='Level of verbosity')
  parser.add_argument('--autoExposure', '-a', action='store_true', help='Do auto exposure')
  
  args, unknown = parser.parse_known_args()
  oname = args.name
  verbose = int(args.verbose)
  outformat = args.format.lower()
  autoExposure = args.autoExposure

  cam = zwo(verbose=verbose)

  prev_gain, prev_exposure = cam.SettingFromLog(set=False)
  gain = int(args.gain) if args.gain is not None else prev_gain
  exposure = int(float(args.exposure)*1000) if args.exposure is not None else prev_exposure

  if autoExposure:
    gain = cam.GetAutoGain()
    exposure = cam.AutoExposure()
  cam.SetGain(gain)
  cam.SetExposure(exposure)
  cam.SetOutName(oname)
  cam.Snap(format=outformat, auto=0, recalculate_each_min=None)

if __name__ == '__main__':
  main()










