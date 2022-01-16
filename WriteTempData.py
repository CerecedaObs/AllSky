'''
 Script to write temperature and humidity data from the allsky sensor into a text file

'''

fdata = '/home/astroberry/allsky/.tempdata.dat'

from DHTsensor import *
import time, datetime

def WriteData():
  timestring = datetime.datetime.now().strftime("%Y %m %d %H %M %S")
  hum, temp = GetTempAndHumSafe(5)
  data = "%s %1.1f %1.1f\n"%(timestring, hum, temp)
  with open(fdata, "a") as f:
    f.write(data)

while 1:
  WriteData()
  time.sleep(5)


