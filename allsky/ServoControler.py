#!/usr/bin/env python3

'''
 This program controls the servo motor to open and close the shell
 To test:
   >> python ServoControler.py open
   >> python ServoControler.py close
'''


from time import sleep
import time, sys, os
import pigpio

from allsky.config import SERVO_PIN, SHELL_LOG

DELAY = 4
POS_OPEN = 580
POS_CLOSED = 1900
STEP_PERIOD = 0.025 # in seconds
STEPS = 40

def interpolate(first, last, x):
    ''' Interpolate ''' 
    return (last - first)*x + first


class ServoControl:
  def __init__(self, pin=SERVO_PIN, verbose=True):
    ''' Initialize servos and angles '''
    self._pin = pin
    self.logname = SHELL_LOG
    self.alt_last  = bool(self.ReadLog()) # boolean open=True
    self.verbose = verbose
    self.pi = pigpio.pi()
    if self.verbose: 
      print('Initial position: ', self.alt_last)
    if self.alt_last:
      if self.verbose: print('  (Open)  ')
    else:
      if self.verbose: print('  (Close) ')

  def IsOpen(self):
    return int(self.ReadLog()) == 1

  def IsClose(self):
    return int(self.ReadLog()) == 0

  def SetVerbose(self, verbose=True):
    ''' Set verbose '''
    self.verbose = verbose

  def WriteLog(self):
    with open(self.logname, 'w') as f:
      f.write("%1.4f"%self.alt_last)

  def ReadLog(self):
    if not os.path.isfile(self.logname):
      return 0.0
    with open(self.logname, 'r') as f:
      r = f.read()
    r = r.replace('\n', '').replace(' ', '')
    try:
      return float(r)
    except:
      print('ERROR: wrong log format')   
      os.system('rm %s'%self.logname)
      return 0.0

  def open(self):
    for i in range(STEPS+1):
      pos = interpolate(POS_CLOSED, POS_OPEN, float(i)/STEPS)
      self.pi.set_servo_pulsewidth(self._pin, pos)
      self.alt_last = True
      sleep(STEP_PERIOD)

  def close(self):
    for i in range(STEPS+1):
      pos = interpolate(POS_OPEN, POS_CLOSED, float(i)/STEPS)
      self.pi.set_servo_pulsewidth(self._pin, pos)
      self.alt_last = False
      sleep(STEP_PERIOD)

  def OpenDome(self):
    self.open()
    self.WriteLog()

  def CloseDome(self):
    self.close()
    self.WriteLog()


###################################################################################

def AllSky_OpenShell():
  SC = ServoControl(verbose=False)
  SC.OpenDome()
  time.sleep(2)
  SC.pi.stop()

def AllSky_CloseShell():
  SC = ServoControl(verbose=False)
  SC.CloseDome()
  time.sleep(2)
  SC.pi.stop()


if __name__=='__main__':
  servo = ServoControl(verbose=True)
  args = sys.argv
  if len(args) == 1:
    print("TEST -- opening and closing shell...")
    while(1):
     servo.OpenDome()
     print('Open shell!')
     time.sleep(2)
     servo.CloseDome()
     print('Close shell')
     time.sleep(2)
  else:
    arg = args[-1]
    if arg.lower() in ['open', 'on']:
      servo.OpenDome()
      print('Open shell!')
      time.sleep(2)
    else:
      servo.CloseDome()
      print('Close shell')
      time.sleep(2)
  exit()   
