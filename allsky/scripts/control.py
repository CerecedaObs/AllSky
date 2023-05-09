from allsky.config import RUNINFOPATH
import json

def UpdateSystem(system, status):
  ''' Update the json file with system status ''' 
  with open(RUNINFOPATH, 'r') as f:
    runinfo = json.load(f)
  runinfo[system] = status
  with open(RUNINFOPATH, 'w') as f:
    json.dump(runinfo, f)


#################################################
### Command control
import argparse

if __name__=='__main__':
  import argparse
  parser = argparse.ArgumentParser(description='Allsky sequencer')
  parser.add_argument('system', type=str, help='system name')
  parser.add_argument('status', type=str, help='or or off')
  args = parser.parse_args()

  system = args.system.lower()
  status = args.status.lower()

  status = True if (status == 'on' or status=='open') else False

  if system == 'allsky' or system.startswith('cam') or system.startswith('zwo') or system.startswith('ccd') or system.startswith('seq'):
    print('Turning %s allsky sequencer'%('on' if status else 'off'))
    UpdateSystem('sequencer', int(status))

  elif system=='shell':
        print('%s shell'%('Opening' if status else 'Closing'))
        UpdateSystem('shell', int(status))

  elif system.startswith('log'):
        print('%s log'%('Starting' if status else 'Stopping'))
        UpdateSystem('logger', int(status))

  elif system.startswith('heat'):
        print('%s heater'%('Starting' if status else 'Stopping'))
        UpdateSystem('heater', int(status))
