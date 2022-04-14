#!/usr/bin/env python

import argparse
import os
import sys
import time
import zwoasi as asi
from astropy.io import fits
from allsky.obscoor import obscoor

from allsky.config import SDK_LIB_PATH, OUTPUT_IMAGES_DIR

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

    # Darks
    self.darkDir = None
    self.darkCorrect = None # Only if night time?

    self.SetOutPath(OUTPUT_IMAGES_DIR)


  ##################################################################################
  ##################################################################################
  def GetAutoExposure(self, fixGain=None):
    ''' Get automatic exposure and gain '''
    self.PrepareVideo()
    self.camera.start_video_capture()
    self.camera.set_control_value(asi.ASI_EXPOSURE, 500000)
    self.SetTimeOut()
    controls = self.camera.get_controls()
    if 'Exposure' in controls and controls['Exposure']['IsAutoSupported']:
      if self.verbose >= 2: print('Enabling auto-exposure mode')
      self.camera.set_control_value(asi.ASI_EXPOSURE, controls['Exposure']['DefaultValue'], auto=True)
    self.camera.set_control_value(controls['AutoExpMaxExpMS']['ControlType'], 10000000) # 10 seconds at maximum

    if 'Gain' in controls and controls['Gain']['IsAutoSupported'] and fixGain is None:
      if self.verbose >= 2: print('Enabling automatic gain setting')
      self.camera.set_control_value(asi.ASI_GAIN,  controls['Gain']['DefaultValue'], auto=True)
      self.camera.set_control_value(controls['AutoExpMaxGain']['ControlType'], 80) # 10 seconds at maximum
    else: #self.camera.set_control_value(asi.ASI_GAIN, fixGain, auto=False)
      if self.verbose: print('Fixing gain to 0')
      self.camera.set_control_value(asi.ASI_GAIN,  fixGain, auto=True)
      self.camera.set_control_value(controls['AutoExpMaxGain']['ControlType'], 0) # 10 seconds at maximum

    sleep_interval = 0.100
    df_last = None
    gain_last = None
    exposure_last = None
    matches = 0
    while True:
      time.sleep(sleep_interval)
      settings = self.camera.get_control_values()
      df = self.camera.get_dropped_frames()
      gain = settings['Gain']
      exposure = settings['Exposure']
      if df != df_last:
        if self.verbose >= 2: print(' > Gain {gain:d}  Exposure: {exposure:f} Dropped frames: {df:d}'.format(gain=settings['Gain'],exposure=settings['Exposure'], df=df))
        if gain == gain_last and exposure == exposure_last:
          matches += 1
        else:
          matches = 0
        if matches >= 5:
          break
        df_last = df
        gain_last = gain
        exposure_last = exposure
    self.camera.stop_video_capture()
    settings = self.camera.get_control_values()
    if self.verbose:
      print('Auto gain    : ', settings['Gain'])
      print('Auto exposure: ', settings['Exposure'])

  def GetRawImage(self):
    ''' Get a numpy image '''
    return self.camera.capture()


  ### Dakrs
  #########################################################################################
  def SetPathDarks(self, path):
    ''' Set path to dark folder '''
    self.darkDir = path

  def SnapDark(self):
    ''' Save a dark frame into the dark folder '''
    pass

  def LoadDark(self, temp, gain, exposure):
    ''' Find the best dark image from the dark folder '''
    pass

  def DarkSubstract(self, image):
    ''' Normalize dark and substract from image '''
    pass



  ### Fits to color, debayer...
  ##########################################################################################
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

  def FitsToJpeg(self, fits):
    ''' Debayern and save to jpeg '''
    pass

  def FitsToTiff(self, fits):
    ''' Debayern and save to tiff '''
    pass


  ### Set methods
  #############################################################################
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

  ### Get methods
  ##################################################################
  def SetPrefix(self, pr):
    self.prefix = pr

  def SetSufix(self, sf):
    self.sufix = sf

  def SetSufixTimeNow(self):
    sufix = self.coor.GetTimeNow("%Y_%m_%d_%H_%M_%S")
    self.SetSufix(sufix)

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

  def GetFileName(self, format='jpg'):
    ''' Crafts the output file name for a given format '''
    while format.startswith('.'): format = format[1:]
    filename = self.GetOutPath() + self.GetOutName() + '.' + format
    return filename

  ### Print
  ##################################################################
  def PrintCameraControls(self):
    ''' Print camera controls '''
    print('Camera controls:')
    controls = self.camera.get_controls()
    for cn in sorted(controls.keys()):
        print('    %s:' % cn)
        for k in sorted(controls[cn].keys()):
          print('        %s: %s' % (k, repr(controls[cn][k])))

  ### Snap
  ###################################################################
  def PrepareSnap(self):
    try:
      # Force any single exposure to be halted
      camera.stop_video_capture()
      camera.stop_exposure()
    except (KeyboardInterrupt, SystemExit):
      raise
    except:
      pass

  def PrepareVideo(self):
    # Enable video mode
    try:
      # Force any single exposure to be halted
      self.camera.stop_exposure()
    except (KeyboardInterrupt, SystemExit):
      raise
    except:
      pass

  def SnapTIFF(self):
    ''' Save a monocolor 16-bit tiff image '''
    self.PrepareSnap()
    if self.verbose: print('Capturing a single 16-bit mono image')
    filename = self.GetFileName('tiff')
    self.camera.set_image_type(asi.ASI_IMG_RAW16)
    self.camera.capture(filename=filename)
    if self.verbose: print('Saved to %s' % filename)

  def SnapJPEG(self):
    ''' Save color jpeg image '''
    self.PrepareSnap()
    filename = self.GetFileName('jpg')
    self.camera.set_image_type(asi.ASI_IMG_RGB24)
    if self.verbose: print('Capturing a single, color image')
    self.camera.capture(filename=filename)
    if self.verbose: print('Saved to %s' % filename)

  def SnapFIT(self):
    ''' Save a FITs file '''
    img = self.GetRawImage()
    hdu = fits.PrimaryHDU(img)
    filename = self.GetFileName('fit')
    header = self.CraftFitsHeader()
    for k in header: hdu.header[k] = header[k]
    if os.path.isfile(filename): os.system('mv %s %s.old'%(filename, filename))
    hdu.writeto(filename)
    if self.verbose: print('Saved to %s' % filename)

  def PrintControlValues(self):
    ''' Print camera control values '''
    print('Camera control values:')
    settings = self.camera.get_control_values()
    for k in sorted(settings.keys()):
      print('  > %s: %s' % (k, str(settings[k])))

  def VideoSnap(self):  
    if self.verbose: print('Enabling video mode')
    self.PrepareVideo()
    self.camera.start_video_capture()
    self.sufix = 'video'
    filename = self.GetFileName('jpg')
    self.camera.set_image_type(asi.ASI_IMG_RGB24)
    self.camera.capture_video_frame(filename=filename)
    if self.verbose: print('Saved to %s' % filename)

  def SaveControlValues(self):
    ''' Save the control values in a txt file '''
    self.sufix = 'settings'
    filename = self.GetFileName('txt')
    settings = self.camera.get_control_values()
    with open(filename, 'w') as f:
        for k in sorted(settings.keys()):
            f.write('%s: %s\n' % (k, str(settings[k])))
    if self.verbose: print('Camera settings saved to %s' % filename)

def main():
  parser = argparse.ArgumentParser(description='Take a pic')
  parser.add_argument('--exposure', '-t',  default=1000, help='Exposure time')
  parser.add_argument('--gain', '-g',  default=10, help='Gain')
  parser.add_argument('--format', '-f',  default='', help='Output format: TIFF, fits, jpg...')
  parser.add_argument('--name', '-o',  default='temp', help='Output name')
  parser.add_argument('--verbose', '-v', default=1, help='Level of verbosity')
  parser.add_argument('--autoExposure', '-a', action='store_true', help='Do auto exposure')
  
  args, unknown = parser.parse_known_args()
  oname = args.name
  verbose = int(args.verbose)
  gain = int(args.gain)
  exposure = int(args.exposure)*1000
  outformat = args.format.lower()
  autoExposure = args.autoExposure

  cam = zwo()
  cam.SetOutName(oname)
  cam.SetGain(gain)
  cam.SetExposure(exposure)
  if autoExposure: 
      print('Auto exposure!')
      if cam.coor.IsNight():
        print('Is night')
        cam.GetAutoExposure()
      else: 
        print('Is day')
        cam.GetAutoExposure(fixGain=0)

  cam.PrintControlValues()
  if outformat in ['jpg', 'jpeg']:
    cam.SnapJPEG()
  elif outformat in ['tif', 'tiff']:
    cam.SnapTIFF()
  else:
    cam.SnapFIT()

if __name__ == '__main__':
  main()










