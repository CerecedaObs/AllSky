'''
 This script runs on and off all the subprocesses needed.
 It check that all the scripts are running when needed and, if not, it starts them on the background.
 It also produces a log file with the status of the scripts and a log database with the status of the system.
'''

import time, datetime, json, os

from allsky.config import DATABASEPATH, ZWO_LOG, SHELL_LOG, LOG_INTERVAL, RUNINFOPATH, BASEPATH
from allsky.DHTsensor import GetTempAndHumSafe

columnNames = ['date', 'humidity', 'temperature', 'CCDgain', 'CCDexp', 'CCDtemp', 'CCDdate', 'sequencer', 'shell', 'heater']

def ReadCamLog():
  with open(ZWO_LOG, 'r') as f:
    log = json.load(f)
  return log

def ReadShellStatus():
    with open(SHELL_LOG, 'r') as f:
      r = f.read()
    r = r.replace('\n', '').replace(' ', '')
    try:
      return int(r)
    except:
      return 0

def ReadSystemStatus():
  ''' Get the status of a system (which is an integer) '''
  with open(RUNINFOPATH, 'r') as f:
    runinfo = json.load(f)
  return int(runinfo['sequencer']), int(runinfo['heater'])

def Log():
  # Check if csv file exist and create it if not
  if not os.path.isfile(DATABASEPATH):
    with open(DATABASEPATH, 'w') as f:
      f.write(','.join(columnNames)+'\n')

  while True:
      # Current time
      now = datetime.datetime.now()

      # Temperature and humidity from DHT sensor
      hum, temp = GetTempAndHumSafe(3)

      # From CCD
      log = ReadCamLog()
      gain = log['GAIN']
      exp  = log['EXPTIME']
      CCDtemp = log['CCDTEMP']
      lastpic_date = log['DATE']
      while isinstance(lastpic_date, str) and lastpic_date.endswith(' '):
        lastpic_date = lastpic_date[:-1]
      lastpic_date = datetime.datetime.strptime(lastpic_date, '%d/%m/%Y %H:%M:%S')

      # CCD status
      seq, heater = ReadSystemStatus()

      # shell status
      shellStatus = ReadShellStatus()

      # Log in a .csv file -- add a column
      with open(DATABASEPATH, 'a') as f:
        f.write('%s,%f,%f,%d,%d,%f,%s,%d,%d,%d\n'%(now.strftime('%d/%m/%Y %H:%M:%S'), hum, temp, gain, exp, CCDtemp, lastpic_date.strftime('%d/%m/%Y %H:%M:%S'), seq, shellStatus, heater))
      
      # sleep
      time.sleep(LOG_INTERVAL)


if __name__ == '__main__':
  Log()