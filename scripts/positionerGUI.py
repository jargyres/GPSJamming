from tkinter import *

from tkinter import messagebox

import numpy as np

import serial

# #https://www.ets-lindgren.com/sites/etsauthor/ProductsManuals/Positioners/2005(1).pdf

ser = serial.Serial('/dev/ttyUSB0')

win = Tk()

win.title("ETS-Lindgren Azimuth Position Model 2005")

win.geometry("500x500")

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

# def seek():
#     degree = seek_entry.get()
#     degree = int(degree)
#     data = "SK{}\n".format(degree)
#     ser.write(data.encode('ascii'))
#     # updateOutput()

def setspeed():
    speed = setspeed_entry.get()
    speed = int(speed)
    data = "S{}\n".format(speed)
    ser.write(data.encode('ascii'))
    updateOutput()

def setpos():
    speed = setpos_entry.get()
    speed = int(speed)
    data = "CP{}\n".format(speed)
    ser.write(data.encode('ascii'))
    updateOutput()

def readpos():
    pos = readpos_entry.get()
    # degree = int(degree)
    for i in range(10):

        data = "CP?\n"
        ser.write(data.encode('ascii'))
        line = ser.readline()
        l = line.decode('utf-8').rstrip()
        readpos_entry.delete(0, END)
        readpos_entry.insert(0,l)

def readspeed():
    # degree = int(degree)
    data = "S?\n"
    ser.write(data.encode('ascii'))
    line = ser.readline()
    l = line.decode('utf-8').rstrip()
    readspeed_entry.delete(0, END)
    readspeed_entry.insert(0,l)

def other():
    l = other_entry.get()
    data = "{}\n".format(l)
    ser.write(data.encode('ascii'))
    updateOutput()

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
                    print(currentPos)
                    if(np.abs(currentPos - degree) < 0.5):
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
                    print(currentPos)
                    if(np.abs(currentPos - degree) < 0.5):
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
l1 = Label(win, text = "Output:")
l1.grid(row=1, column=1)
output_entry.grid(row=1, column=2)

# seek_entry=Entry(win, width= 25)
# l1 = Label(win, text = "Degree(000.0 - 999.9):")
# l1.grid(row=2, column=1)
# seek_entry.grid(row=2, column=2)
# B = Button(win, text ="Seek", command = seek)
# B.grid(row=2, column=3)

readpos_entry=Entry(win, width= 25)
l1 = Label(win, text = "Degree:")
l1.grid(row=3, column=1)
readpos_entry.grid(row=3, column=2)
B = Button(win, text ="Read Position", command = readpos)
B.grid(row=3, column=3)

setpos_entry=Entry(win, width= 25)
l1 = Label(win, text = "Degree(000.0 - 999.9):")
l1.grid(row=4, column=1)
setpos_entry.grid(row=4, column=2)
B = Button(win, text ="Set Position", command = setpos)
B.grid(row=4, column=3)

setspeed_entry=Entry(win, width= 25)
l1 = Label(win, text = "Speed(0-3):")
l1.grid(row=5, column=1)
setspeed_entry.grid(row=5, column=2)
B = Button(win, text ="Set Speed", command = setspeed)
B.grid(row=5, column=3)

readspeed_entry=Entry(win, width= 25)
l1 = Label(win, text = "Speed:")
l1.grid(row=6, column=1)
readspeed_entry.grid(row=6, column=2)
B = Button(win, text ="Read Speed", command = readspeed)
B.grid(row=6, column=3)

other_entry=Entry(win, width= 25)
l1 = Label(win, text = "Other:")
l1.grid(row=7, column=1)
other_entry.grid(row=7, column=2)
B = Button(win, text ="Send Command", command = other)
B.grid(row=7, column=3)

counterclockwise_entry=Entry(win, width= 25)
l1 = Label(win, text = "Degree:")
l1.grid(row=8, column=1)
counterclockwise_entry.grid(row=8, column=2)
B = Button(win, text ="Seek Counter Clockwise", command = seekCC)
B.grid(row=8, column=3)

clockwise_entry=Entry(win, width= 25)
l1 = Label(win, text = "Degree:")
l1.grid(row=9, column=1)
clockwise_entry.grid(row=9, column=2)
B = Button(win, text ="Seek Clockwise", command = seekCW)
B.grid(row=9, column=3)

win.mainloop()

ser.close()
