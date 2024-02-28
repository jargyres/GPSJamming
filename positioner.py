import serial

# #https://www.ets-lindgren.com/sites/etsauthor/ProductsManuals/Positioners/2005(1).pdf

ser = serial.Serial('/dev/ttyUSB0')

# # data = "SK-10.0\n"


def seek(degree, ser):
    data = "SK{}\n".format(degree)
    ser.write(data.encode('ascii'))


seek(0, ser)

# data = "SK0\n"
# # data = "CP0\n"
# # data = "DIR?\n"


# ser.write(data.encode('ascii'))

# line = ser.readline()

# l = line.decode('utf-8').rstrip()

# print(l)

ser.close()
