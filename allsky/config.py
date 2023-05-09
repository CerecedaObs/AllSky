import allsky
BASEPATH = list(allsky.__path__)[0][:-len('allsky')]
RUNINFOPATH = BASEPATH+'data/allsky_run.json'
CHECK_INTERVAL = 10 # seconds

# LOGS
DATABASEPATH = BASEPATH+'data/allsky_data.csv'
LOG_INTERVAL = 30 # seconds

# ZWO
SDK_LIB_PATH = BASEPATH + 'data/libASICamera2.so'
ZWO_LOG = BASEPATH + 'data/zwoStatus.log'
ZWO_EXPMAX = 10 # seconds
ZWO_GAINMAX = 50 

# DHT Sensor
DHT_SENSOR_TYPE = 11
DHT_GPIO_PIN = 23 # GPIO23, pin 16

# HEATER
HEATER_PIN = 11 # GPIO17
HEATER_LOG = BASEPATH + 'data/heaterStatus.log'

# SHELL SERVO
SERVO_PIN = 18 #12 # GPIO18
SHELL_LOG = BASEPATH + 'data/shellPos.log'

# Coordinates
CERECEDA_ALLSKY_LAT =  43.25916375853605 
CERECEDA_ALLSKY_LON = -6.603491884147439

OUTPUT_IMAGES_DIR = '/media/astroberry/E8C6-3E053/pics/'
OUTPUT_TIMELAPSE_DIR = '/media/astroberry/E8C6-3E053/timelapses/'
OUTPUT_DARKS_DIR = '/media/astroberry/E8C6-3E053/darks/'

TIME_INTERVAL_DAY = 30
TIME_INTERVAL_NIGHT = 30
