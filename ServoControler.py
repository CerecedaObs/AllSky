import RPi.GPIO as GPIO
import time, sys, os

'''
 This program controls the servo motor to open and close the shell
 To test: 
   >> python ServoControler.py open
   >> python ServoControler.py close

 # Servo connected to pin 11

'''

PIN_SERVO = 11

# Set GPIO numbering mode
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Set servos to their pins
GPIO.setup(PIN_SERVO,GPIO.OUT)

class ServoControl:
  def __init__(self, pin=PIN_SERVO, verbose=False):
    ''' Initialize servos and angles '''
    self.servo = GPIO.PWM(pin,50) 
    self.servo.start(0)
    self.open_angle = 115.
    self.close_angle = 0.
    self.alt0 = 0.
    self.logname = '.shellPos.log'
    self.alt_last  = self.ReadLog()
    print('Initial position: ', self.alt_last)
    if self.alt_last == self.open_angle:
      print('  (Open)  ')
    elif self.alt_last == self.close_angle:
      print('  (Close) ')
    self.verbose = verbose
    self.step = 20 # from 0 to 100
    self.slow = True
    #self.GoToStandbyPosition()

  def SetStep(self, step=10):
    self.step = step

  def SetVerbose(self, verbose=True):
    ''' Set verbose '''
    self.verbose = verbose

  def SetAlt0(self, alt0=''):
    ''' Calibrate altitude angle '''
    if alt0 == '': alt0 = self.alt_last
    self.alt0 = alt0
    if self.verbose: print('Calibrating altitude angle to %1.2fo'%self.alt0)

  def LocalAltitude(self, ang=0):
    ''' Calculates local (calibrated) values
        Altitude goes from 0 to 180
    '''
    return self.alt0 + ang

  def GoToAlt(self, alt):
    ''' Change the altitude '''
    oalt = self.LocalAltitude(alt)
    if alt <  10: alt = 10
    if alt > 170: alt = 170
    self.MoveServo(self.servo, oalt, self.alt_last)
    return oalt

  def GoTo(self, alt):
    ''' Moves to alt, azm '''
    self.GoToAlt(alt)

  def MoveServo(self, servo, angle, initial_angle):
    if self.slow:
      i = initial_angle
      f = angle
      nextAngle = i
      step = self.step/10 # degrees
      while abs(nextAngle - f) > step:
        sign = ((f-i)/abs(f-i))
        nextAngle = float(i + step*sign)
        servo.ChangeDutyCycle(2+(nextAngle/18))
        i = nextAngle
        time.sleep(0.02)
        servo.ChangeDutyCycle(2+(nextAngle/18))
      servo.ChangeDutyCycle(2+(angle/18))
    else:
      servo.ChangeDutyCycle(2+(angle/18))
    time.sleep(0.05)
    servo.ChangeDutyCycle(0)
    self.alt_last = angle
    self.WriteLog()

  def GoToAngleRaw(self, alt):
    ''' Input must be in degrees and in correct ranges '''
    self.GoToAlt(alt)
    if self.verbose: print('Pointing to [%1.2fo]'%(alt))

  def GoToAngle(self, alt):
    ''' Input must be in degrees and in correct ranges '''
    self.GoToAngleRaw(alt)

  def Clean(self):
    ''' Clean things up at the end '''
    self.servo.stop()
    GPIO.cleanup()
    print("Finishing servo control")

  ########## Interaction
  def GoToStandbyPosition(self):
    ''' Goes to STANDBY by looking to the zenit '''
    self.OpenDome()
    time.sleep(1)

  def SayYes(self):
    ''' Says yes '''
    for i in range(3):
      self.GoToAlt(65)
      time.sleep(0.01)
      self.GoToAlt(40)
      time.sleep(0.1)

  def CloseDome(self):
    self.GoToAlt(self.close_angle)
    time.sleep(0.1)

  def OpenDome(self):
    self.GoToAlt(self.open_angle)
    time.sleep(0.1)

  def WriteLog(self):
    with open(self.logname, 'w') as f:
      f.write("%1.4f"%self.alt_last)
  
  def ReadLog(self):
    if not os.path.isfile(self.logname):
      return 0.0
    with open(self.logname, 'r') as f:
      r = f.read()
    r = r.replace('\n', '').replace(' ', '')
    try:
      return float(r)
    except:
      print('ERROR: wrong log format')   
      os.system('rm %s'%self.logname)
      return 0.0
    return float(r)


if __name__=='__main__':
  servo = ServoControl()
  args = sys.argv
  if len(args) == 1:
    print("TEST -- opening and closing shell...")
    while(1):
     servo.OpenDome()
     print('Open shell!')
     time.sleep(2)
     servo.CloseDome()
     print('Close shell')
     time.sleep(2)
  else:
    arg = args[-1]
    if arg.lower() in ['open', 'on']:
      servo.OpenDome()
      print('Open shell!')
      time.sleep(2)
    else:
      servo.CloseDome()
      print('Close shell')
      time.sleep(2)
  exit()   
