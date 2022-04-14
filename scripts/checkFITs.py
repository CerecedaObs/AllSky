import sys, os
from astropy.io import fits

args = sys.argv[1:]
if len(args) == 0:
  print ("Give the name of a .fit image")
  exit()

imgpath = args[0]
img = fits.open(imgpath)[0] # Assume primary HDU
print(img.header.values)
