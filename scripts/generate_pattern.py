import numpy as np
import serial
import adi   #Make sure libiio and py-adi and their dependencies are all installed. 
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading

ser = serial.Serial('/dev/ttyUSB0')

sdr = adi.FMComms5(uri='ip:analog.local')  #This has to match the address of the Zynq board
freq = 3000000000
sdr.rx_lo = freq  #Change as desired 
sdr.rx_lo_chip_b = freq
samplerate = 60000000
sdr.sample_rate = samplerate
bandwidth = 18000000
sdr.rx_rf_bandwidth = bandwidth

angleLimit = 60


array_element_distance = 0.04996540966


pattern_theta_list = []
pattern_list = []

beamformAngle = -0.523599

def w_mvdr(theta, r, d, Nr):
   a = np.exp(-2j * np.pi * d * np.arange(Nr) * np.sin(theta)) # steering vector in the desired direction theta
   a = a.reshape(-1,1) # make into a column vector (size 3x1)
   R = r @ r.conj().T # Calc covariance matrix. gives a Nr x Nr covariance matrix of the samples
   Rinv = np.linalg.pinv(R) # 3x3. pseudo-inverse tends to work better/faster than a true inverse
   w = (Rinv @ a)/(a.conj().T @ Rinv @ a) # MVDR/Capon equation! numerator is 3x3 * 3x1, denominator is 1x3 * 3x3 * 3x1, resulting in a 3x1 weights vector
   return w


def beamform(data_rx, angle):
    
    w = w_mvdr(angle, data_rx, d=array_element_distance, Nr=4)

    return w.conj().T @ data_rx

def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def Get_Combined_RX_Pwr(data):

    # dataC = data[0] + data[1] + data[2] + data[3]
    dataC = data

    NUM_SAMPLES = 1024

    max_pwr_search_size = 30
    # f = np.linspace(-0.5 * samplerate, 0.5 * samplerate, len(dataC))
    f_carrier = np.linspace(-0.5 * samplerate, 0.5 * samplerate, NUM_SAMPLES) + (freq)

    data_fft = (20 * np.log10(np.abs(np.fft.fftshift(np.fft.fft(dataC))) / NUM_SAMPLES)) - 20
    carrier_data = [np.transpose(f_carrier), data_fft]
    carrier_data = np.asanyarray(carrier_data)

    # indexes = indices(carrier_data[0], lambda x: x > freq - 1e6 and x < freq + 1e6)
    indexes = np.linspace(NUM_SAMPLES/2 - max_pwr_search_size, NUM_SAMPLES/2 + max_pwr_search_size, dtype=int)

    pwr=max(data_fft[indexes])
    
    return pwr


def CWReceive():
    
    data = "CR\n"
    ser.write(data.encode('ascii'))
    data = "CW\n"
    ser.write(data.encode('ascii'))

    pos = ""
    while(True):
        data = "CP?\n"
        ser.write(data.encode('ascii'))
        line = ser.readline()
        l = line.decode('utf-8').rstrip()
        if l:
            if l != "\x06":
                if is_float(l):
                    pos = float(l)
                    x = sdr.rx()
                    rx = np.asarray(x)
                    # pwr_db = Get_Combined_RX_Pwr(rx)
                    new_x = beamform(rx, beamformAngle).reshape(len(x[0]))
                    pwr_db = Get_Combined_RX_Pwr(new_x)

                    pattern_theta_list.append(pos)
                    pattern_list.append(pwr_db)

                    print("{} deg = {} dB".format(pos, pwr_db))


                    if(np.abs(float(l) - angleLimit) < 0.2):
                        break
    while(True):
        data = "ST\n"
        ser.write(data.encode('ascii'))
        data = "DIR?\n"
        ser.write(data.encode('ascii'))
        line = ser.readline()
        l = line.decode('utf-8').rstrip()

        if l:
            if l != "\x06":
                if l == 'N':
                    break

    data = "ST\n"
    ser.write(data.encode('ascii'))

def CCReceive():
    
    cc_angle_limit = 360.0 - angleLimit
    data = "CR\n"
    ser.write(data.encode('ascii'))
    data = "CC\n"
    ser.write(data.encode('ascii'))

    pos = ""
    while(True):
        data = "CP?\n"
        ser.write(data.encode('ascii'))
        line = ser.readline()
        l = line.decode('utf-8').rstrip()
        if l:
            if l != "\x06":
                if is_float(l):
                    pos = float(l)
                    x = sdr.rx()
                    rx = np.asarray(x)

                    new_x = beamform(rx, beamformAngle).reshape(len(x[0]))
                    pwr_db = Get_Combined_RX_Pwr(new_x)

                    pattern_theta_list.append(pos)
                    pattern_list.append(pwr_db)
                    print("{} deg = {} dB".format(pos, pwr_db))

                    if(np.abs(float(l) - cc_angle_limit) < 0.2):
                        break
    while(True):
        data = "ST\n"
        ser.write(data.encode('ascii'))
        data = "DIR?\n"
        ser.write(data.encode('ascii'))
        line = ser.readline()
        l = line.decode('utf-8').rstrip()

        if l:
            if l != "\x06":
                if l == 'N':
                    break

    data = "ST\n"
    ser.write(data.encode('ascii'))




CCReceive()
CWReceive()

#turn into array
pattern_theta = np.asarray(pattern_theta_list)
#turn into radians
pattern_theta = np.deg2rad(pattern_theta)
#turn into array
pattern = np.asarray(pattern_list)
sorted_theta_ind = np.argsort(pattern_theta)

pattern_theta = pattern_theta[sorted_theta_ind]
pattern = pattern[sorted_theta_ind]

pattern, idx = np.unique(pattern, return_index=True)
pattern_theta = pattern_theta[idx]

max_pwr = np.max(pattern)
pattern = pattern - max_pwr
fig = plt.figure()
ax = fig.add_subplot(111, polar=True)
ax.set_theta_direction('clockwise')
ax.scatter(pattern_theta, pattern, s=1)
ax.set_thetalim(-np.pi / 2, np.pi/2)
ax.set_thetagrids([-90, -60, -30, 0,30, 60,90])
ax.set_rticks([0, -10,-20, -30, -40],labels= ["0dB", "-10dB","-20dB","-30dB","-40dB"])
ax.set_theta_zero_location("N")
ax.grid(True,which="minor",linestyle= ":")
ax.grid(True,which="major",linewidth= 1.5)
ax.minorticks_on()
plt.show()