#!/usr/bin/env python3

'''
 This script runs on and off all the subprocesses needed.
 It check that all the scripts are running when needed and, if not, it starts them on the background.
'''

from allsky.config import RUNINFOPATH, CHECK_INTERVAL, BASEPATH
import json, subprocess, time

def ReadSystemStatus(system):
  ''' Get the status of a system (which is an integer) '''
  with open(RUNINFOPATH, 'r') as f:
    runinfo = json.load(f)
  return int(runinfo[system])

def IsProcessRunning(script_name):
  ''' Chech if a pyhon script is running '''
  proc = subprocess.Popen(['pgrep', '-f', script_name], stdout=subprocess.PIPE)
  return proc.stdout.readlines()

def Run(script_name, log_file=None):
  ''' Run a script on the background '''
  if log_file is not None:
    with open(log_file, 'a') as f:
        subprocess.Popen(['python3', script_name], stderr=f)
  else:
    subprocess.Popen(['python3', script_name])

def StopProcess(script_name):
  ''' Stop a process '''
  subprocess.Popen(['pkill', '-f', script_name])


#### Heater -- on/off
from allsky.Heater import Heater
heater = Heater()

#### Shell -- open/close
from allsky.ServoControler import ServoControl
SC = ServoControl()

# Processes:
scripts = {'sequencer': BASEPATH+'allsky/scripts/Sequencer.py', 'logger':BASEPATH+'allsky/Logger.py'}
actions = ['shell', 'heater']

if __name__ == "__main__":
    config_file = "commands.txt"

    while True:
        # Sequencer, logger
        for process, script in scripts.items():
          status = ReadSystemStatus(process)
          isRunning = IsProcessRunning(script)
          if status and not isRunning:
            Run(script, log_file=BASEPATH+'allsky/logs/%s.log'%process)
          elif not status and isRunning:
            StopProcess(script)

        # Shell
        shell_status = ReadSystemStatus('shell')
        is_open = SC.IsOpen()
        if shell_status and not is_open:
          SC.OpenDome()
        elif not shell_status and is_open:
          SC.CloseDome()

        # Heater
        heater_status = ReadSystemStatus('heater')
        is_on = heater.ReadLog()
        if heater_status and not is_on:
          heater.On()
        elif not heater_status and is_on:
          heater.Off()

        time.sleep(CHECK_INTERVAL)
