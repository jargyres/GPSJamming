from tkinter import *

from tkinter import messagebox

import numpy as np

import serial

import adi   #Make sure libiio and py-adi and their dependencies are all installed. 
import time
import matplotlib.pyplot as plt
from scipy import signal
import pandas as pd
import re
import csv

# #https://www.ets-lindgren.com/sites/etsauthor/ProductsManuals/Positioners/2005(1).pdf

ser = serial.Serial('/dev/ttyUSB0')

win = Tk()

win.title("ETS-Lindgren Azimuth Position Model 2005")

win.geometry("500x500")

sdr = adi.FMComms5(uri='ip:analog.local')  #This has to match the address of the Zynq board
freq = 3000000000
sdr.rx_lo = freq  #Change as desired 
sdr.rx_lo_chip_b = freq
samplerate = 60000000
sdr.sample_rate = samplerate
bandwidth = 18000000
sdr.rx_rf_bandwidth = bandwidth

angleLimit = 90

def indices(a, func):
    return [i for (i, val) in enumerate(a) if func(val)]

def Get_RX_dB(data):

    dataC = data[0] + data[1] + data[2] + data[3]

    NUM_SAMPLES = 1024
    # f = np.linspace(-0.5 * samplerate, 0.5 * samplerate, len(dataC))
    f_carrier = np.linspace(-0.5 * samplerate, 0.5 * samplerate, NUM_SAMPLES) + (freq)

    data_fft = (20 * np.log10(np.abs(np.fft.fftshift(np.fft.fft(dataC))) / NUM_SAMPLES)) - 20
    carrier_data = [np.transpose(f_carrier), data_fft]
    carrier_data = np.asanyarray(carrier_data)

    indexes = indices(carrier_data[0], lambda x: x > freq - 1e6 and x < freq + 1e6)

    pwr=max(data_fft[indexes])
    
    return pwr

def updateOutput():
    while True:
        l = ser.readline().decode('utf-8').strip()  # Decode and strip whitespace
        if l:  # Check if the line is non-empty
            output_entry.delete(0, END)
            output_entry.insert(0,l)
            break  # Exit the loop once a non-empty line is found


def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def setpos():
    speed = setpos_entry.get()
    speed = int(speed)
    data = "CP{}\n".format(speed)
    ser.write(data.encode('ascii'))
    updateOutput()


def updatePosition():
    for i in range(20):
        data = "CP?\n"
        ser.write(data.encode('ascii'))
        line = ser.readline()
        l = line.decode('utf-8').rstrip()
        output_entry.delete(0, END)
        output_entry.insert(0,l)

def seekCC():

    degree = counterclockwise_entry.get()
    degree = float(degree)
    data = "CR\n"
    ser.write(data.encode('ascii'))
    data = "CC\n"
    ser.write(data.encode('ascii'))

    while(True):
        data = "CP?\n"
        ser.write(data.encode('ascii'))
        line = ser.readline()
        l = line.decode('utf-8').rstrip()

        if l:
            if l != "\x06":
                if is_float(l):
                    currentPos = float(l)
                    # print(currentPos)
                    output_entry.delete(0, END)
                    output_entry.insert(0,l)
                    if(np.abs(currentPos - degree) < 0.2):
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

    # updatePosition()


def seekCW():

    degree = clockwise_entry.get()
    degree = float(degree)
    data = "CR\n"
    ser.write(data.encode('ascii'))
    data = "CW\n"
    ser.write(data.encode('ascii'))

    while(True):
        data = "CP?\n"
        ser.write(data.encode('ascii'))
        line = ser.readline()
        l = line.decode('utf-8').rstrip()

        if l:
            if l != "\x06":
                if(is_float(l)):
                    currentPos = float(l)
                    # print(currentPos)
                    output_entry.delete(0, END)
                    output_entry.insert(0,l)
                    if(np.abs(currentPos - degree) < 0.2):
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

    updatePosition()

def readpos():
    while(True):
        data = "CP?\n"
        ser.write(data.encode('ascii'))
        line = ser.readline()
        l = line.decode('utf-8').rstrip()

        if l:
            if l != "\x06":
                if(is_float(l)):
                    output_entry.delete(0, END)
                    output_entry.insert(0,l)
                    break
                    


def receive():

    pos = ""
    while(True):
        data = "CP?\n"
        ser.write(data.encode('ascii'))
        line = ser.readline()
        l = line.decode('utf-8').rstrip()

        if l:
            if l != "\x06":
                if(is_float(l)):
                    pos = l
                    break
                    

    pos = pos.replace('.', '_')
    print(pos)
    l = savecsv_entry.get()
    x = sdr.rx()
    rx = np.asarray(x)
    df = pd.DataFrame(x)
    df.to_csv(l + pos + ".csv", header=False, index=False)

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
                    pos = l
                    pos = pos.replace('.', '_')
                    x = sdr.rx()
                    rx = np.asarray(x)
                    pwr_db = Get_RX_dB(rx)
                    datawrite = ['{:f}'.format(float(l)), '{:06.10f}'.format(pwr_db)]

                    with open('data.csv', 'a') as writeFile:
                        writer = csv.writer(writeFile)
                        writer.writerow(datawrite)
                    writeFile.close()

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
                    pos = l
                    pos = pos.replace('.', '_')
                    print(pos)
                    ll = savecsv_entry.get()
                    x = sdr.rx()
                    rx = np.asarray(x)
                    pwr_db = Get_RX_dB(rx)
                    datawrite = ['{:f}'.format(float(l)), '{:06.10f}'.format(pwr_db)]

                    with open('data.csv', 'a') as writeFile:
                        writer = csv.writer(writeFile)
                        writer.writerow(datawrite)
                    writeFile.close()
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
    
output_entry=Entry(win, width= 25)
l1 = Label(win, text = "Current Position:")
l1.grid(row=1, column=1)
output_entry.grid(row=1, column=2)

counterclockwise_entry=Entry(win, width= 25)
l1 = Label(win, text = "Degree:")
l1.grid(row=2, column=1)
counterclockwise_entry.grid(row=2, column=2)
B = Button(win, text ="Seek Counter Clockwise", command = seekCC)
B.grid(row=2, column=3)

clockwise_entry=Entry(win, width= 25)
l1 = Label(win, text = "Degree:")
l1.grid(row=3, column=1)
clockwise_entry.grid(row=3, column=2)
B = Button(win, text ="Seek Clockwise", command = seekCW)
B.grid(row=3, column=3)

setpos_entry=Entry(win, width= 25)
l1 = Label(win, text = "Degree(000.0 - 999.9):")
l1.grid(row=4, column=1)
setpos_entry.grid(row=4, column=2)
B = Button(win, text ="Set Position", command = setpos)
B.grid(row=4, column=3)

# setpos_entry=Entry(win, width= 25)
# l1 = Label(win, text = "Degree(000.0 - 999.9):")
# l1.grid(row=4, column=1)
# setpos_entry.grid(row=4, column=2)
B = Button(win, text ="Update Position", command = readpos)
B.grid(row=1, column=3)

savecsv_entry=Entry(win, width= 25)
l1 = Label(win, text = "Filename:")
l1.grid(row=5, column=1)
savecsv_entry.grid(row=5, column=2)
# B = Button(win, text ="RX to CSV", command = receive)
# B.grid(row=5, column=3)


B = Button(win, text ="Start CW RX", command = CWReceive)
B.grid(row=6, column=1)


B = Button(win, text ="Start CC RX", command = CCReceive)
B.grid(row=6, column=3)

win.mainloop()

ser.close()
