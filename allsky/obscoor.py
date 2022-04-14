'''
 Class to get current time and coordinates for the observatory, sunset, sunrise and other space-time features

'''


import time, datetime
import pytz
import astroplan
import astropy.units as u
from astropy.time import Time

from allsky.config import CERECEDA_ALLSKY_LAT, CERECEDA_ALLSKE_LON

class obscoor:
  def __init__(self, latitude=CERECEDA_ALLSKY_LAT, longitude=CERECEDA_ALLSKE_LON):
    self.latitude = latitude
    self.longitude = longitude
    self.t0 = time.time()
    self.timezone = 'Europe/Madrid'
    self.tz = pytz.timezone(self.timezone)
    self.obs = astroplan.Observer(longitude=longitude*u.deg, latitude=latitude*u.deg, elevation=700*u.m, name='Cereceda', timezone=self.timezone)
    self.std_format = "%d/%m/%Y %H:%M:%S %Z"

  def GetAstroTimeNow(self, utc=False):
    time = Time(datetime.datetime.utcnow()) if utc else Time(datetime.datetime.now())
    return time

  def GetTimeNow(self, format=None):
    if format is None: format = self.std_format
    now = datetime.datetime.now()
    s = now.strftime(format)
    return s

  def GetToday(self, format="%d/%m/%Y"):
    today = datetime.date.today()
    s = today.strftime(format)
    return s

  def GetDeltaTime(self):
    return time.time() - self.t0

  def IsNight(self):
    return self.obs.is_night(self.GetAstroTimeNow(utc=True))

  def GetSunsetTime(self):
    sunset = self.obs.sun_set_time(self.GetAstroTimeNow()).datetime
    sunset = sunset.replace(tzinfo=pytz.utc) 
    sunset = sunset.astimezone(self.tz)
    return sunset

  def GetSunriseTime(self):
    sunrise = self.obs.sun_rise_time(self.GetAstroTimeNow()).datetime
    sunrise = sunrise.replace(tzinfo=pytz.utc) 
    sunrise = sunrise.astimezone(self.tz)
    return sunrise

if __name__ == '__main__':
  o = obscoor()
  t = o.GetAstroTimeNow()
  print('Now: ', o.GetTimeNow(), ' -- ' + 'Is night!' if o.IsNight() else 'is not night yet...')
  print('Sun set  time: ', o.GetSunsetTime().strftime(o.std_format)  )
  print('Sun rise time: ', o.GetSunriseTime().strftime(o.std_format)  )
