from allsky.config import OUTPUT_DARKS_DIR
import os

def GetDarkImg(temp, exp, gain=0):
    '''
    Temp in degrees C
    Exp in seconds
    Gain from 0 to 100
    '''
    temp = (int(temp*10))
    exp  = (int(exp ))
    gain = (int(gain))
    if exp == 0:
        print("Exposure time cannot is less than 0.5s --> We don't need darks for this")
        return None
    # list dir to get all temps
    available_temps = []
    for t in os.listdir(OUTPUT_DARKS_DIR):
        try:
            available_temps.append(int(t))
        except:
            pass
    # Get closest temp in available temps
    temp = min(available_temps, key=lambda x:abs(x-temp))
    opath = os.path.join(OUTPUT_DARKS_DIR, str(temp))

    # list dir to get all exps
    available_exps = []
    for t in os.listdir(opath):
        try:
            available_exps.append(int(t))
        except:
            pass
    # Get closest exp in available exps
    exp = min(available_exps, key=lambda x:abs(x-exp))
    opath = os.path.join(opath, str(exp))

    # list dir to get all gains
    available_gains = []
    for t in os.listdir(opath):
        try:
            available_gains.append(int(t))
        except:
            pass
    # Get closest gain in available gains
    gain = min(available_gains, key=lambda x:abs(x-gain))
    opath = os.path.join(opath, str(gain))
    oname = "%s_%s_%s_master.fit"%(temp, gain, exp)
    opath = os.path.join(opath, oname)
    if not os.path.exists(opath):
        print('Dark not found: ', opath)
        return None
    return opath

print(GetDarkImg(30, 1, 0))