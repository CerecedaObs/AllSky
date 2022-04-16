from allsky.run import *
from allsky.ServoControler import *

def Interpret(command):
  ''' Interpret the command '''
  if command == 'OpenShell':
    AllSky_OpenShell()
  elif command == 'CloseShell':
    AllSky_CloseShell()
  elif command == 'SequencerOn':
    Allsky_TurnOn()
  elif command == 'SequencerOff':
    Allsky_TurnOff()
  else: return False
  return True
