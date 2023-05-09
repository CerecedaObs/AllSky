from astral.sun import sun
from astral import LocationInfo
import ephem
import datetime
import pytz

# Set your location
location = LocationInfo()
location.latitude = 43.25920030758968
location.longitude = -6.603432266146361
location.timezone = "Europe/Madrid" #"UTC"

# Get the current time
tz = pytz.timezone(location.timezone)
current_time = datetime.datetime.now(tz)

# Get sun information
s = sun(location.observer, date=current_time)

print(f"Current time: {current_time}")
print(f"Sunrise: {s['sunrise']}")
print(f"Sunset: {s['sunset']}")
print(f"Day time: {s['sunrise'] <= current_time <= s['sunset']}")

# Get moon information
moon = ephem.Moon()
observer = ephem.Observer()
observer.lat, observer.lon = str(location.latitude), str(location.longitude)
moon.compute(observer)

moon_phase = moon.moon_phase * 100  # Moon phase percentage
print(f"Moon phase: {moon_phase:.2f}%")

# Get visible planets
planets = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
visible_planets = []

for planet_name in planets:
    planet = ephem.__dict__[planet_name]()
    print(ephem.__dict__)
    planet.compute(observer)

    # Check if the planet is above the horizon and visible
    if planet.alt > 0 and planet.mag < 10:
        visible_planets.append(planet_name)

print("Visible planets:", visible_planets)
