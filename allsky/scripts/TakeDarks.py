'''
This script automatically takes darks to create a library. We want to have:
> Exp time   : from 1 to 20s, each 1s
> Temperature: from 0 to 50º, each 0.5º
> Gain from 0 to 100, each 10
> Individual darks: 10 per point

'''

import os
from allsky.zwo import zwo
from allsky.config import OUTPUT_DARKS_DIR, OUTPUT_IMAGES_DIR
from allsky.obscoor import obscoor
from allsky.ServoControler import ServoControl
from astropy.io import fits
import time, glob
import numpy as np
import cv2



def create_master_dark(dark_files, output_file, method='median', gain=None, exposure_time=None, temperature=None):
    darks = []
    for dark_file in dark_files:
        with fits.open(dark_file) as dark_fits:
            darks.append(dark_fits[0].data)

    master_dark = np.median(darks, axis=0) if method == 'median' else np.mean(darks, axis=0)
    master_hdu = fits.PrimaryHDU(master_dark)

    if gain is not None:
        master_hdu.header['GAIN'] = gain
    if exposure_time is not None:
        master_hdu.header['EXPTIME'] = exposure_time
    if temperature is not None:
        master_hdu.header['TEMP'] = temperature

    master_hdu.writeto(output_file, overwrite=True)

def GetDarksPath(temp, exp, gain, idx=None):
    temp = str(int(temp))
    exp  = str(int(exp ))
    gain = str(int(gain))
    idx  = str((idx))
    opath = os.path.join(OUTPUT_DARKS_DIR, temp)
    opath = os.path.join(opath, exp)
    opath = os.path.join(opath, gain)
    if not os.path.exists(opath): 
        os.makedirs(opath)
    if not idx is None:
        oname = "%s_%s_%s_%s.fit"%(temp, gain, exp, idx)
        opath = os.path.join(opath, oname)
    return opath

def take_darks():
  while cover.IsClose() and obs.IsAstronomicalTwilight():
    temp = round( cam.GetTemperature() / 5 ) * 5

    for exp in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]:
        for gain in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
            for i in range(10):
                oname = GetDarksPath(temp, exp, gain, i)
                if os.path.exists(oname):
                    time.sleep(0.1)
                    continue
                path, name = os.path.split(oname)
                cam.SetOutPath(path)
                cam.SetOutName(name)
                cam.SetGain(gain)
                cam.SetExposure(exp)
                print('Taking dark for TEMP %i - EXP %i - GAIN %i ---> %i'%(temp, exp, gain, i))
                cam.SnapFIT()
                time.sleep(5)


# Merge Darks
def merge_darks():
    for exp in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]:
        for gain in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
            for temp in range(200, 400, 5):
                oname = GetDarksPath(temp, exp, gain, 'master')
                opath, fname = os.path.split(oname)
                if os.path.exists(opath):
                    imgs = []
                    for f in os.listdir(opath):
                        if f.lower().endswith('.fit') or f.lower().endswith('fits'):
                            if 'master' in f: continue
                            imgs.append(os.path.join(opath, f))
                    if len(imgs)==10:
                        # Merge darks
                        print('Merging darks for TEMP %i - EXP %i - GAIN %i'%(temp, exp, gain))
                        create_master_dark(imgs, oname, method='median', gain=int(gain), exposure_time=float(exp), temperature=float(temp)/10)
                        print('Created master file: ', oname)
                        time.sleep(0.1)
                        print('Removing individual darks for TEMP %i - EXP %i - GAIN %i'%(temp, exp, gain))
                        for f in imgs:
                            os.remove(f)

def removeEmptyFolders(): 
    # walk though OUTPUT_DARKS_DIR subdirs and check if they are empty
    for root, dirs, files in os.walk(OUTPUT_DARKS_DIR, topdown=False):
        for name in dirs:
            path = os.path.join(root, name)
            if not os.listdir(path):
                print('Removing empty folder: ', path)
                os.rmdir(path)


def find_closest_dark(temperature, exposure_time, gain):
    ''' Find the closest dark to a given temperature, exposure time and gain '''
    if temperature < 100: temperature = int(temperature*10)
    exposure_time = int(exposure_time)
    gain = int(gain)
    min_temperature_diff = float('inf')
    min_exposure_diff = float('inf')
    min_gain_diff = float('inf')
    closest_dark = None

    ftemp = 0; fexp = 0; fgain = 0
    for folder in glob.glob(os.path.join(OUTPUT_DARKS_DIR, '*')):
        temp_diff = abs(int(os.path.basename(folder)) - temperature)
        if temp_diff < min_temperature_diff:
            min_temperature_diff = temp_diff
            ftemp = os.path.basename(folder)
            for exp_folder in glob.glob(os.path.join(folder, '*')):
                exp_diff = abs(int(os.path.basename(exp_folder)) - exposure_time)
                if exp_diff < min_exposure_diff:
                    min_exposure_diff = exp_diff
                    fexp = os.path.basename(exp_folder)
                    for gain_folder in glob.glob(os.path.join(exp_folder, '*')):
                        gain_diff = abs(int(os.path.basename(gain_folder)) - gain)
                        if gain_diff < min_gain_diff:
                            min_gain_diff = gain_diff
                            fgain = os.path.basename(gain_folder)

    closest_dark = os.path.join(OUTPUT_DARKS_DIR, str(ftemp), str(fexp), str(fgain), '%s_%s_%s_master.fit'%(ftemp, fgain, fexp))
    if not os.path.exists(closest_dark):
        print('ERROR: Something went wrong... Could not find a dark for temperature %i, exposure time %i and gain %i'%(temperature, exposure_time, gain))
        print('Closest dark: ', closest_dark, ' -- does not exist!')
        return None
        
    return closest_dark

def dark_correct_img(imgpath):
    ''' Apply dark to image '''
    # Read the light image header
    with fits.open(imgpath) as light_image:
        header = light_image[0].header
        temperature = int(header.get('CCDTEMP', 0))
        exposure_time = int(header.get('EXPTIME', 0))
        gain = int(header.get('GAIN', 0))
    print('Looking for dark for TEMP %i - EXP %i - GAIN %i'%(temperature, exposure_time, gain))

    # Find the closest dark image
    closest_dark_path = find_closest_dark(temperature, exposure_time, gain)
    print('Found closest dark: ', closest_dark_path)

    # Correct the light image with the dark
    with fits.open(imgpath) as light_image:
        light_data = light_image[0].data

    with fits.open(closest_dark_path) as dark_image:
        dark_data = dark_image[0].data

    corrected_data = light_data - dark_data

    # Return the corrected FITS image
    corrected_image = fits.PrimaryHDU(corrected_data, header=header)
    return corrected_image


def white_balance(img):
    result = np.zeros_like(img)
    for i in range(3):  # Iterate through R, G, and B channels
        channel = img[:, :, i]
        channel_median = np.median(channel)
        scale = 32768.0 / channel_median
        result[:, :, i] = np.clip(channel * scale, 0, 65535)
    return result.astype(np.uint16)

def remove_hot_pixels(img, kernel_size=3):
    median_filtered = cv2.medianBlur(img, kernel_size)
    return median_filtered

def debayer(fit_image, outpath=None):
    ''' Debayer a FITS image and save it as a JPEG '''
    if isinstance(fit_image, str):
        with fits.open(fit_image) as image:
            data = image[0].data
        jpeg_output_path = os.path.splitext(fit_image)[0] + '.jpg'
    else:
        data = fit_image.data
        jpeg_output_path = outpath if outpath is not None else 'debayered_image.jpg'
        if outpath.lower().endswith('.fit') or outpath.lower().endswith('.fits'):
            jpeg_output_path = os.path.splitext(outpath)[0] + '.jpg'
    

    # Normalize the data to the range 0-65535 (16-bit)
    data_normalized = ((data - data.min()) / (data.max() - data.min()) * 65535).astype(np.uint16)

    # Debayer the image
    debayered_image = cv2.cvtColor(data_normalized, cv2.COLOR_BAYER_RG2RGB)

    # Apply white balance
    balanced_image = white_balance(debayered_image)

    # Remove hot pixels
    filtered_image = remove_hot_pixels(balanced_image)

    # Convert to 8-bit and save as JPEG
    debayered_image_8bit = (filtered_image / 256).astype(np.uint8)
    cv2.imwrite(jpeg_output_path, debayered_image_8bit)
    print('Saved debayered image: ', jpeg_output_path)

                    
    

if __name__=='__main__':
    #obs = obscoor()
    #cam = zwo(verbose=False)
    #cover = ServoControl()
    #take_darks()
    #merge_darks()
    #removeEmptyFolders()
    path = OUTPUT_IMAGES_DIR
    #list dir and take latest created dir
    dirs = [os.path.join(path, d) for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    dirs.sort(key=os.path.getctime, reverse=True)
    path = dirs[0]
    # take latest .fit file
    files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.lower().endswith('.fit')]
    files.sort(key=os.path.getctime, reverse=True)
    imgpath = files[0]
    print('Correcting image: ', imgpath)
    corrected = dark_correct_img(imgpath)
    # debayer
    debayer(corrected, outpath=imgpath)

