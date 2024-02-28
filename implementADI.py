from ADI import ADI
import time
import numpy as np
import ctypes

sdr = ADI()

sdr.set_rf_frequency(3005000000)

sdr.set_samplerate(30e6)

# sdr.set_tx_frequency(3100000000)

# sdr.set_tx_frequency(4095000000)


# sdr.set_gain_tx(-30)

# sdr.MultiChipSync(ctypes.c_uint(0))

# sdr.phaseSync()

# time.sleep(1)

# sdr.createSignal()

# sdr.tx_transmit(0, 0.5)

# time.sleep(0.01)

data = sdr.receive([0, 1, 2, 3])

# data = data * 1/(2 ** 14)

# print(data)

sdr.plot_recieved(data)
sdr.plotTimeDomain(data)