# From https://linuxtut.com/en/6947fd91260d9475bd93/
from astropy.io import fits
import sys, os

args = sys.argv[1:]
if len(args) == 0:
  print ("Give the name of a .fit image")
  exit()

imgpath = args[0]

hdul = fits.open(imgpath)
img = fits.open(imgpath)[0]
print(img.header.values)

imgdat = img.data
print(imgdat)
import cv2
#dst = cv2.cvtColor(imgdat, cv2.COLOR_BayerBG2BGR)
#cv2.imwrite('test_debayer.jpg', dst)
