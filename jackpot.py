import serial
port = serial.Serial("COM4",115200) # serial port and baud rate for dell xps laptop
port.write(str.encode('r200'))  