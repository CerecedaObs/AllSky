import os, sys
import argparse
import pathlib
import pytz
from datetime import datetime, timedelta, date
from allsky.config import *
from allsky.obscoor import obscoor

class TimelapseCreator:
  def __init__(self, time=None, mode=None, end=None, fps=15, verbose=1):
    ''' 
      Time format: string "%Y_%m_%d" or "%Y_%m_%d_%H_%M_%S"
    '''
    self.SetInputPath(OUTPUT_IMAGES_DIR)
    self.SetOutputPath(OUTPUT_TIMELAPSE_DIR)
    self.SetOutName('timelapse')
    self.SetVerbose(verbose)

    self.coor = obscoor()
    self.SetImgExt('jpg')
    self.SetOutExt('mp4')

    self.aspect = None
    self.vbitrate = 8000000
    self.scale = None
    self.fps = self.SetFrameRate(fps)
    self.tempFilePics = '.timelapsePicList.txt'

    if time==None: # By default, yesterday
      time = str(date.today() - timedelta(days=1))
    self.SetInputTime(time)
    self.SetMode(mode)
    if end is not None: self.SetEndTime(end)

  ###########################################################
  ### Sets
  def SetInputPath(self, path):
    if path is None: return
    self.path = path

  def SetOutputPath(self, path):
    if path is None: return
    self.outpath = path

  def SetOutName(self, name):
    if name is None: return
    self.outname = name

  def SetOutPrefix(self, pr):
    self.prefix = pr

  def SetOutSufix(self, sf):
    self.sufix = sf

  def SetOutExt(self, ext):
    while ext.endswith('.'): ext = ext[:-1]
    self.outext = ext

  def SetImgExt(self, ext):
    while ext.endswith('.'): ext = ext[:-1]
    self.imgext = ext

  def SetVerbose(self, verbose=1):
    self.verbose = verbose

  def SetFrameRate(self, rate=15):
    self.fps = rate


  ###########################################################################################
  ### Craft times and modes
  def TransformTime(self, time):
    if isinstance(time, datetime): return time # Only transforms if str
    time = time.replace('-', '_').replace(' ', '_').replace(':', '_').replace('.', '_').replace('/', '_')
    time = time.replace('__', '_')
    if   time.count('_') == 2:
      dtime = datetime.strptime(time, "%Y_%m_%d")
    elif time.count('_') == 5:
      dtime = datetime.sptime(time, "%Y_%m_%d_%H_%M_%S")
    else:
      print("WARNING: time format unknown (%s)"%time)
      dtime = None
    return dtime

  def SetInputTime(self, time=None):
    if isinstance(time, str): self.time_str = time
    if time is None: return
    self.time = self.TransformTime(time)
    self.coor.GetSunriseTime(self.time)
    self.sunrise = self.coor.GetSunriseTime(self.time)
    self.sunset = self.coor.GetSunsetTime(self.time)

  def SetEndTime(self, time):
    self.end = self.TransformTime(time)

  def SetMode(self, mode=None):
    # Standard modes: 
    # - full: [date of sunrise] from sunrise to sunrise 
    # - daylight: [dateof sunrise] from sunrise to sunset
    # - night: [date of sunset] from sunset to sunrise
    # - week: [date of sunrise start day]
    # - month: [date of sunrise start day]
    # - year: [date of sunrise start day]
    # - time: [date and time of a single moment] Gets pics for all days at the single time, from the starting day
    if mode is None:
      self.mode = None
      return
    self.mode = mode.lower()
    self.SetOutPrefix(mode)
    if   mode == 'full':
      self.start = self.sunrise 
      self.end   = self.sunrise+timedelta(days=1)
    elif mode == 'daylight':
      self.start = self.sunrise
      self.end   = self.sunset
    elif mode == 'night':
      self.start = self.sunset
      self.end   = self.sunrise+timedelta(days=1)
    elif mode == 'week':
      self.start = self.sunrise
      self.end   = self.sunrise+timedelta(days=7)
    elif mode == 'month':
      self.start = self.sunrise
      self.end   = self.sunrise+timedelta(days=30)
    else:
      if self.verbose >= 2: print("WARNING: unknown mode")
      self.start = self.time
      self.end   = self.time+timedelta(days=1)

  #############################################################################################
  ### Paths and files
  def GetOutName(self):
    name = self.prefix + '_' if self.prefix is not None else ''
    name += self.filename
    name += '_'+self.sufix if self.sufix is not None else ''
    return name

  def GetOutPath(self):
    if not self.outpath.endswith('/'): self.outpath += '/'
    if not os.path.isdir(self.outpath):
      os.system('mkdir -p %s'%self.outpath)
      if self.verbose >= 2: print('Created output directory: ', self.outpath)
    return self.outpath

  def GetFileName(self, ext=None):
    ''' Crafts the output file name for a given format '''
    if ext is not None: self.SetOutExt(ext)
    filename = self.GetOutPath() + self.GetOutName() + '.' + self.outext
    return filename

  def GetListOfFiles(self, startDate=None, endDate=None):
    ''' Gets a list of pics in the input directory sorted by date. The ranges depend on the given mode and the starting date '''
    if startDate is None: startDate = self.start
    if endDate   is None:   endDate = self.end
    listOfFiles = []
    # Find all the files with a given extension in a directory and subdirectories
    for f in  pathlib.Path(self.path).glob('*.'+self.imgext):
      ftime = datetime.fromtimestamp( os.path.getmtime(self.path+f.name) )
      ftime = ftime.replace(tzinfo=pytz.timezone(self.coor.timezone))
      if (startDate <= ftime <= endDate): 
        listOfFiles.append(self.path+f.name)
    return listOfFiles

  def CreateListOfFiles(self, listOfFiles=None):
    ''' Write the files in a .txt file '''
    if listOfFiles is None: listOfFiles = self.GetListOfFiles()
    oname = self.GetOutPath()+self.tempFilePics
    with open(oname, 'w') as fo:
      for path in listOfFiles:
        fo.write(path+'\n')
    if verbose>=2: print('Saving temp .txt with files in ', oname)

  #############################################################################################
  ### Producing the timelapse
  def GetTypeMencoder(self):
    inputtype = 'jpeg' if self.imgext == 'jpg' else self.imgext
    return "type=%s:fps=%i"%(inputtype, self.fps)

  def CraftCommand(self):
    # mencoder -nosound -ovc lavc -lavcopts vcodec=mpeg4:mbd=2:trell:aspect=16/9:vbitrate=8000000 -vf scale=1920:1080 -mf type=jpeg:fps=14 mf://@archivos.txt -o timelapse.avi
    command='mencoder -nosound -ovc lavc -lavcopts vcodec=mpeg4:mbd=2:trell:aspect=16/9:vbitrate=%i -vf -mf %s mf://@archivos.txt -o timelapse.avi'%(self.vbitrate, self.GetTypeMencoder(), self.tempFilePics, self.GetFileName())

  def ExecuteCommand(self, command=None):
    if command is None: command = self.CraftCommand()
    if verbose: print('Executing command: ', command)
    os.system(command)

  def Produce(self):
    self.CreateListOfFiles()
    command = self.CraftCommand()
    # self.ExecuteCommand(command)

if __name__ == '__main__':

  parser = argparse.ArgumentParser(description='Create a timelapse with mencoder')

  parser.add_argument('--path', '-p', default=None,  help='Path to pics')
  parser.add_argument('--outpath', default=None, help='Output path')
  parser.add_argument('--outname', '-o', default='temp_timelapse.mp4', help='Output file')
  parser.add_argument('--rateOfFrames', '-r', default=10, help='frames per second')
  parser.add_argument('--start', default=None, help="start date")
  parser.add_argument('--end', default=None, help="end date")
  parser.add_argument('--mode', '-m', default="full", help="end date")
  parser.add_argument('--verbose', '-v', default=1, help="end date")

  args = parser.parse_args()
  path = args.path
  out  = args.outname
  opath = args.outpath
  start = args.start
  end   = args.end
  mode  = args.mode
  verbose = int(args.verbose)
  rate = int(args.rateOfFrames)

  tl = TimelapseCreator(start, mode, end, verbose=verbose)
  tl.SetFrameRate(rate)
  tl.SetOutputPath(opath)
  tl.SetOutName(out)
  tl.Produce()
