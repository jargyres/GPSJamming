import adi   #Make sure libiio and py-adi and their dependencies are all installed. 
import time
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import pandas as pd    


sdr = adi.FMComms5(uri='ip:analog.local')  #This has to match the address of the Zynq board
sdr.rx_lo = 3000000000  #Change as desired 
sdr.rx_lo_chip_b = 3000000000
sdr.sample_rate = 60000000
sdr.rx_rf_bandwidth = 18000000


#print(sdr.rx_hardwaregain)

# Read properties
fs = int(sdr.sample_rate)
print("RX LO %s" % (sdr.rx_lo))

# Plot data
for r in range(20):
    x = sdr.rx()
    print(type(x))
	
    f, Pxx_den = signal.periodogram(x[0], fs)
    plt.clf()
    plt.semilogy(f, Pxx_den)
    f, Pxx_den = signal.periodogram(x[1], fs)
    plt.semilogy(f, Pxx_den)

    f, Pxx_den = signal.periodogram(x[2], fs)
    plt.semilogy(f, Pxx_den)

    f, Pxx_den = signal.periodogram(x[3], fs)
    plt.semilogy(f, Pxx_den)

    plt.ylim([1e-7, 1e2])
    plt.xlabel("frequency [Hz]")
    plt.ylabel("PSD [V**2/Hz]")
    plt.draw()
    plt.pause(0.05)
    time.sleep(0.1)

plt.show()
# save the unnormalized data
print(type(x))
rx = np.asarray(x)
print(type(rx))
print(rx.shape)
df = pd.DataFrame(x)
df.to_csv('anechoic_13.csv', header=False, index=False) #Name of the file at which recieved data is saved

