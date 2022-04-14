from allsky.config import BASEPATH

logpath = BASEPATH+'data/allsky_run.log'

def Allsky_ReadStatus():
  with open(logpath) as f:
    r = f.read()
  return r

def Allsky_IsOn():
  return Allsky_ReadStatus().lower() == 'on'

def Allsky_IsOff():
  return not Allsky_ReadStatus().lower() == 'on'

def Allsky_TurnOn():
  with open(logpath, 'w') as f:
    f.write('on')

def Allsky_TurnOff():
  with open(logpath, 'w') as f:
    f.write('off')

import sys
if __name__ == '__main__':
  args = sys.argv[1:]
  if len(args) == 0:
      print('on or off?')
      exit()
  if   args[0].lower() == 'on' : Allsky_TurnOn()
  elif args[0].lower() == 'off': Allsky_TurnOff()
  else:
      print('on or off?')
