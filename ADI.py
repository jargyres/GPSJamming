import time
import adi
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import time
import threading
from ctypes import *
class ADI:


    def __init__(self):
        """
        Create an instance of the FMComms5
        """
        self.sdr = adi.FMComms5(uri='ip:analog.local')

        self.sdr.rx_enabled_channels = [0, 1, 2, 3]

        # self.phaseSyncFile = "./libad9361-iio/phaseSync.so"

        # self.phasesync = CDLL(self.phaseSyncFile)

        self.context = self.sdr._ctx._context

        # self.multichipSyncFile = "./libad9361-iio/multichipSync.so"

        # self.multichipsync = CDLL(self.multichipSyncFile)

    def set_rf_frequency(self, frequency):
        """
        Set the frequency that all of our rx will receive at
        """

        self.sdr.rx_lo = frequency

        self.sdr.rx_lo_chip_b = frequency
    
    def set_tx_frequency(self, frequency):

        """
        Set the frequency that all our our tx will transmit at
        """

        self.sdr.tx_lo = frequency

        self.sdr.tx_lo_chip_b = frequency

        self.sdr.tx_cyclic_buffer = True

    def set_gain_tx(self, gain):
        """
        Set the hardwage gain of the transmit
        """

        self.sdr.tx_hardwaregain = gain

        self.sdr.tx_hardwaregain_chip_b = gain

        self.sdr.gain_control_mode = "slow_attack"

        self.sdr.gain_control_mode_chip_b = "slow_attack"

    def set_samplerate(self, samplerate):
        """
        Set the samplerate of our board
        """

        self.sdr.sample_rate = samplerate
    
    def receive(self, port):
        """
        Returns the data in the form of row vectors
        according to the order in which you passed the ports
        Ex: recieve([0, 1, 2, 3]) would be\n
        row 0 = port 0\n 
        row 1 = port 1\n 
        row 2 = port 2\n 
        row 3 = port 3\n
        """

        x = self.sdr.rx()

        data = np.empty([len(port), len(x[0])], dtype=complex)

        for i in range(len(port)):

            data[i] = x[i]

        return data

    def createSignal(self):

        """
        Creates an array of size 1024 of our iq data\n
        """

        N = 1024

        fs = int(self.sdr.sample_rate)

        fc = 40000000

        ts = 1 / float(fs)

        t = np.arange(0, N * ts, ts)

        i = np.cos(2 * np.pi * t * fc) * 2 ** 14

        q = np.sin(2 * np.pi * t * fc) * 2 ** 14

        self.iq = i + 1j * q

        fc = -30000000

        i = np.cos(2 * np.pi * t * fc) * 2 ** 14

        q = np.sin(2 * np.pi * t * fc) * 2 ** 14

        self.iq2 = i + 1j * q
    
    def transmit(self, port, Time):
        
        self.sdr.tx_destroy_buffer()

        if(port == 0 or port == 1):

            self.sdr.tx_enabled_channels = [0, 1]

        elif(port == 2 or port == 3):

            self.sdr.tx_enabled_channels = [2, 3]

        self.sdr.tx([self.iq, self.iq2])

        time.sleep(Time)
    
    def tx_transmit(self, port, Time):
        """
        Starts a new thread to transmit our data created with createSignal()\n
        We start a new thread so as to not freeze up our execution waiting for the\n
        transmit to be done
        """

        thread = threading.Thread(target=self.transmit, args=(port, Time))

        thread.start()

    def transmit_and_receive(self, portRX, portTX):
        """
        Transmit our data made from createSignal() and recieve moments later\n
        This returns the same shape of data as receive(ports[])
        """

        self.tx_transmit(portTX, 0.2)

        time.sleep(0.05)

        data = self.receive(portRX)

        return data

    def plot_recieved(self, data):
        """
        Plots the PSD of the received data\n
        If the data is from multiple ports it will plot the separate data in different colors
        """

        if(len(data) == 1):

            f, Pxx_den = signal.periodogram(data[0], self.sdr.sample_rate, return_onesided=False)

            plt.semilogy(f , Pxx_den)

        if(len(data) == 2):

            f, Pxx_den = signal.periodogram(data[0], self.sdr.sample_rate, return_onesided=False)

            plt.semilogy(f , Pxx_den)

            f1, Pxx_den1 = signal.periodogram(data[1], self.sdr.sample_rate, return_onesided=False)

            plt.semilogy(f1 , Pxx_den1)

        if(len(data) == 3):

            f, Pxx_den = signal.periodogram(data[0], self.sdr.sample_rate, return_onesided=False)

            plt.semilogy(f , Pxx_den)

            f, Pxx_den = signal.periodogram(data[1], self.sdr.sample_rate, return_onesided=False)

            plt.semilogy(f , Pxx_den)

            f, Pxx_den = signal.periodogram(data[2], self.sdr.sample_rate, return_onesided=False)

            plt.semilogy(f , Pxx_den)

        if(len(data) == 4):

            f, Pxx_den = signal.periodogram(data[0], self.sdr.sample_rate, return_onesided=False)

            plt.semilogy(f , Pxx_den)

            f, Pxx_den = signal.periodogram(data[1], self.sdr.sample_rate, return_onesided=False)

            plt.semilogy(f , Pxx_den)

            f, Pxx_den = signal.periodogram(data[2], self.sdr.sample_rate, return_onesided=False)

            plt.semilogy(f , Pxx_den)

            f, Pxx_den = signal.periodogram(data[3], self.sdr.sample_rate, return_onesided=False)

            plt.semilogy(f , Pxx_den)

        plt.ylim([1e-7, 1e2])

        plt.xlabel("frequency [Hz]")

        plt.ylabel("PSD [V**2/Hz]")

        plt.draw()

        plt.show()

    def plotTimeDomain(self, data):
        """
        Plots the PSD of the received data\n
        If the data is from multiple ports it will plot the separate data in different colors
        """
        # plt.specgram(data[0], NFFT=1024, Fs=self.sdr.sample_rate);
        # plt.title("Spectogram of file");
        # plt.xlabel("Time")
        # plt.ylabel("Frequency")
        # plt.show()
        # plt.scatter(np.real(data[0]), np.imag(data[0]))
        # f_carrier = []
        # data_fft = []
        if(len(data) == 1):
            fig, ax = plt.subplots(2)
            fig.suptitle("Signals in time domain")
            ax[0].plot(np.linspace(0, 1, len(data[0])), np.real(data[0]))
            ax[0].set_title("Real")
            ax[1].plot(np.linspace(0, 1, len(data[0])), np.imag(data[0]))
            ax[1].set_title("Imaginary")
            plt.tight_layout()
        if(len(data) == 2):
            fig, ax = plt.subplots(2)
            fig.suptitle("Signals in time domain")
            ax[0].plot(np.linspace(0, 1, len(data[0])), np.real(data[0]))
            ax[0].plot(np.linspace(0, 1, len(data[1])), np.real(data[1]))

            ax[0].set_title("Real")
            ax[1].plot(np.linspace(0, 1, len(data[0])), np.imag(data[0]))
            ax[1].plot(np.linspace(0, 1, len(data[1])), np.imag(data[1]))

            ax[1].set_title("Imaginary")
        if(len(data) == 3):
            fig, ax = plt.subplots(2)
            fig.suptitle("Signals in time domain")
            ax[0].plot(np.linspace(0, 1, len(data[0])), np.real(data[0]))
            ax[0].plot(np.linspace(0, 1, len(data[1])), np.real(data[1]))
            ax[0].plot(np.linspace(0, 1, len(data[2])), np.real(data[2]))

            ax[0].set_title("Real")
            ax[1].plot(np.linspace(0, 1, len(data[0])), np.imag(data[0]))
            ax[1].plot(np.linspace(0, 1, len(data[1])), np.imag(data[1]))
            ax[1].plot(np.linspace(0, 1, len(data[2])), np.imag(data[2]))

            ax[1].set_title("Imaginary")
        if(len(data) == 4):
            fig, ax = plt.subplots(2)
            fig.suptitle("Signals in time domain")
            ax[0].plot(np.linspace(0, 1, len(data[0])), np.real(data[0]))
            ax[0].plot(np.linspace(0, 1, len(data[1])), np.real(data[1]))
            ax[0].plot(np.linspace(0, 1, len(data[2])), np.real(data[2]))
            ax[0].plot(np.linspace(0, 1, len(data[3])), np.real(data[3]))

            ax[0].set_title("Real")
            ax[1].plot(np.linspace(0, 1, len(data[0])), np.imag(data[0]))
            ax[1].plot(np.linspace(0, 1, len(data[1])), np.imag(data[1]))
            ax[1].plot(np.linspace(0, 1, len(data[2])), np.imag(data[2]))
            ax[1].plot(np.linspace(0, 1, len(data[3])), np.imag(data[3]))

            ax[1].set_title("Imaginary")

        plt.tight_layout()
        fig.set_size_inches(9, 7, forward=True)
        plt.show()
    # def phaseSync(self):
        
    #     self.phasesync.ad9361_fmcomms5_phase_sync(self.context, self.sdr.rx_lo)

    # def MultiChipSync(self, flags):
    #     self.multichipsync.ad9361_fmcomms5_multichip_sync(self.context, flags)