'''
  This script uses the Adafruit_DHT module to read data from the DHT module (temperature and humidity reader)
  To test:
    >> python3 DHTsensor.py

  To read humidity and temperature from a program, use:
    hum, temp = GetTempAndHumSafe(nit=3, nsec=3)
  where it takes nit measurements each nsec seconds
'''

import time
import Adafruit_DHT

GPIO_PIN = 2
DHT_SENSOR_TYPE = 11

def GetTemperature():
  time.sleep(1)
  h, t = Adafruit_DHT.read_retry(DHT_SENSOR_TYPE, GPIO_PIN)
  return t

def GetHumidity():
  time.sleep(1)
  h, t = Adafruit_DHT.read_retry(DHT_SENSOR_TYPE, GPIO_PIN)
  return h

def GetTempAndHum():
  time.sleep(1)
  h, t = Adafruit_DHT.read_retry(DHT_SENSOR_TYPE, GPIO_PIN)
  return h, t

def GetTempAndHumSafe(nit=1):
  hum=[]; temp=[]
  count = 0
  while count < nit:
    h, t = Adafruit_DHT.read_retry(DHT_SENSOR_TYPE, GPIO_PIN)
    time.sleep(1)
    if h is None or temp is None: continue
    else:
      hum.append(h)
      temp.append(t)
      count+=1
  return sum(hum)/len(hum), sum(temp)/len(temp)

if __name__ == '__main__':
  print('Printing temperature and humidity...')
  while 1:
    h, t = Adafruit_DHT.read_retry(DHT_SENSOR_TYPE, GPIO_PIN)
    print('Temp = ', t,', Hum = ', h, ' %')
    time.sleep(1)

