'''
 Class to get current time and coordinates for the observatory, sunset, sunrise and other space-time features

'''


import time, datetime
import pytz
import astroplan
import astropy.units as u
from astropy.time import Time
import ephem
import matplotlib.pyplot as plt
import numpy as np

from allsky.config import CERECEDA_ALLSKY_LAT, CERECEDA_ALLSKY_LON

class obscoor:
  def __init__(self, latitude=CERECEDA_ALLSKY_LAT, longitude=CERECEDA_ALLSKY_LON):
    self.latitude = latitude
    self.longitude = longitude
    self.t0 = time.time()
    self.timezone = 'Europe/Madrid'
    self.tz = pytz.timezone(self.timezone)
    self.obs = astroplan.Observer(longitude=longitude*u.deg, latitude=latitude*u.deg, elevation=700*u.m, name='Cereceda', timezone=self.timezone)
    self.std_format = "%d/%m/%Y %H:%M:%S %Z"
    self.moon = ephem.Moon()
    self.ephemobs = ephem.Observer()
    self.ephemobs.lat, self.ephemobs.lon = str(CERECEDA_ALLSKY_LAT), str(CERECEDA_ALLSKY_LON)
    self.moon.compute(self.ephemobs)

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

  def GetSunsetTime(self, some_time=None):
    if some_time is None: some_time = (self.GetAstroTimeNow())
    elif not isinstance(some_time, Time): some_time = Time(some_time) 
    sunset = self.obs.sun_set_time(some_time).datetime
    sunset = sunset.replace(tzinfo=pytz.utc) 
    sunset = sunset.astimezone(self.tz)
    return sunset

  def GetSunriseTime(self, some_time=None):
    if some_time is None: some_time = (self.GetAstroTimeNow())
    elif not isinstance(some_time, Time): some_time = Time(some_time) 
    sunrise = self.obs.sun_rise_time(some_time).datetime
    sunrise = sunrise.replace(tzinfo=pytz.utc) 
    sunrise = sunrise.astimezone(self.tz)
    return sunrise

  def IsDayButCloseToSunsetSunrise(self, some_time=None, delta_hours=1):
    ''' Check if it is daytime but we are within delta_hours hours from sunset or sunrise '''
    if some_time is None: some_time = (self.GetAstroTimeNow())
    elif not isinstance(some_time, Time): some_time = Time(some_time)
    sunset = self.GetSunsetTime(some_time)
    sunrise = self.GetSunriseTime(some_time)
    if some_time < sunset and some_time > sunset - delta_hours*datetime.timedelta(hours=1): return True
    if some_time > sunrise and some_time < sunrise + delta_hours*datetime.timedelta(hours=1): return True
    return False

  def IsAstronomicalTwilight(self):
    current_time = Time.now()

    # Calculate the evening and morning astronomical twilight times for the current date
    evening_astronomical_twilight = self.obs.twilight_evening_astronomical(current_time, which='nearest')
    morning_astronomical_twilight = self.obs.twilight_morning_astronomical(current_time, which='nearest')

    # Check if the current time is between the evening and morning astronomical twilight times
    if evening_astronomical_twilight < current_time < morning_astronomical_twilight:
        return True
    else:
        return False

  def IsNauticalTwilight(self):
    current_time = Time.now()

    # Calculate the evening and morning nautical twilight times for the current date
    evening_nautical_twilight = self.obs.twilight_evening_nautical(current_time, which='nearest')
    morning_nautical_twilight = self.obs.twilight_morning_nautical(current_time, which='nearest')

    # Check if the current time is between the evening and morning nautical twilight times
    if evening_nautical_twilight < current_time < morning_nautical_twilight and not self.IsAstronomicalTwilight():
        return True
    else:
        return False

  def GetMoonPhase(self):
    return self.moon.moon_phase*100

  def GetVisiblePlanets(self):
    # Get visible planets
    planets = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
    visible_planets = []

    for planet_name in planets:
        planet = ephem.__dict__[planet_name]()
        planet.compute(self.ephemobs)

        # Check if the planet is above the horizon and visible
        if planet.alt > 0 and planet.mag < 10:
            visible_planets.append(planet_name)
    return visible_planets


def IsNight(obs, time):
  return obs.is_night(time)

def IsAstronomicalTwilight(obs, time):
  evening_astronomical_twilight = obs.twilight_evening_astronomical(time, which='nearest')
  morning_astronomical_twilight = obs.twilight_morning_astronomical(time, which='nearest')
  if evening_astronomical_twilight < time < morning_astronomical_twilight: return True
  else: return False

def IsNauticalTwilight(obs, time):
  evening_nautical_twilight = obs.twilight_evening_nautical(time, which='nearest')
  morning_nautical_twilight = obs.twilight_morning_nautical(time, which='nearest')
  if evening_nautical_twilight < time < morning_nautical_twilight and not IsAstronomicalTwilight(obs, time): return True
  else: return False

if __name__ == '__main__':
  o = obscoor()
  obs = o.obs
  t = o.GetAstroTimeNow()
  print('Is day but close to sunset/sunrise: ', o.IsDayButCloseToSunsetSunrise())
  print('Now: ', o.GetTimeNow(), ' -- ' + 'Is night!' if o.IsNight() else 'is not night yet...')
  print('Sun set  time: ', o.GetSunsetTime().strftime(o.std_format)  )
  print('Sun rise time: ', o.GetSunriseTime().strftime(o.std_format)  )
  print('Moon phase: %1.1f'%(o.GetMoonPhase()) , '%')
  print('Visible planets: ', o.GetVisiblePlanets())
  t = t - 12*u.hour
  t0 = t.datetime.timestamp()
  h = []; isnight = []; isastronomicaltwilight = []; isnauticaltwilight = []
  for i in range(24*2):
    t = t + 30*u.minute
    h.append(t.datetime.timestamp() - t0)
    isnight.append(IsNight(obs, t))
    isastronomicaltwilight.append(IsAstronomicalTwilight(obs, t))
    isnauticaltwilight.append(IsNauticalTwilight(obs, t))
  # h --> time to float
  plt.plot(h, isnight, label='is night')
  plt.plot(h, isastronomicaltwilight, label='is astronomical twilight')
  plt.plot(h, isnauticaltwilight, label='is nautical twilight')
  plt.legend()
  plt.savefig('test.png')

