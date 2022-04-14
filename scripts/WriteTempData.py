fdata = '/home/astroberry/python/.tempdata.dat'

from allsky.DHTsensor import *
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


