import adi   #Make sure libiio and py-adi and their dependencies are all installed. 
import numpy as np


sdr = adi.FMComms5(uri='ip:analog.local')  #This has to match the address of the Zynq board
freq = 3000000000
sdr.rx_lo = freq  #Change as desired 
sdr.rx_lo_chip_b = freq
samplerate = 60000000
sdr.sample_rate = samplerate
bandwidth = 18000000
sdr.rx_rf_bandwidth = bandwidth
array_element_distance = 0.04996540966




def Get_Combined_RX_Pwr(dataC):

    # dataC = data[0] + data[1] + data[2] + data[3]

    NUM_SAMPLES = 1024

    max_pwr_search_size = 30
    # f = np.linspace(-0.5 * samplerate, 0.5 * samplerate, len(dataC))
    f_carrier = np.linspace(-0.5 * samplerate, 0.5 * samplerate, NUM_SAMPLES) + (freq)

    data_fft = (20 * np.log10(np.abs(np.fft.fftshift(np.fft.fft(dataC))) / NUM_SAMPLES)) - 20
    carrier_data = [np.transpose(f_carrier), data_fft]
    carrier_data = np.asanyarray(carrier_data)

    indexes = np.linspace(NUM_SAMPLES/2 - max_pwr_search_size, NUM_SAMPLES/2 + max_pwr_search_size, dtype=int)

    pwr=max(data_fft[indexes])
    
    return pwr


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

x = sdr.rx()
x = np.asarray(x)
print(np.shape(x[0] + x[1] + x[2] + x[3]))
new_x = beamform(x, 0).reshape(len(x[0]))
print(np.shape(new_x))
print(Get_Combined_RX_Pwr(x[0] + x[1] + x[2] + x[3]))
print(Get_Combined_RX_Pwr(new_x))


