import os
import time
import spidev
import re
import string
import smbus
import serial


#Define some device parameters
I2C_ADDR = 0x27
LCD_WIDTH = 16

#Define some device constants
LCD_CHR = 1
LCD_CMD = 0

LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
LCD_LINE_3 = 0x94
LCD_LINE_4 = 0xD4

LCD_BACKLIGHT = 0x08 #On
#LCD_BACKLIGHT = 0X00 #Off

#Timing Constants
E_PULSE = 0.0005
E_DELAY = 0.0005

#Open I2C Interface
#bus = smbus.SMBus(0) #Rev 2 under Pi uses 0
bus = smbus.SMBus(1) #Rev 2 upper Pi uses 1

def lcd_init() :
    lcd_byte(0x33,LCD_CMD) # 110011 Initialise
    lcd_byte(0x32,LCD_CMD) # 110010 Initialise
    lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
    lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
    lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
    lcd_byte(0x01,LCD_CMD) # 000001 Clear display
    time.sleep(E_DELAY)

def lcd_byte(bits, mode) :
    # Send byte to data pins
    # bits = the data
    # mode = 1 for data
    #        0 for command

    bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
    bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT

    # High bits
    bus.write_byte(I2C_ADDR, bits_high)
    lcd_toggle_enable(bits_high)

    # Low bits
    bus.write_byte(I2C_ADDR, bits_low)
    lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits) :
    # Toggle Enable
    time.sleep(E_DELAY)
    bus.write_byte(I2C_ADDR, (bits | ENABLE))
    time.sleep(E_DELAY)
    bus.write_byte(I2C_ADDR, (bits & ~ENABLE))
    time.sleep(E_DELAY)

def lcd_string(message, line) :
    # Send string to display

    message = message.ljust(LCD_WIDTH," ")
    lcd_byte(line, LCD_CMD)

    for i in range(LCD_WIDTH) :
        lcd_byte(ord(message[i]),LCD_CHR)
    

#Channel Setting
Channel_12V = 0
Channel_5V = 2
Channel_4V = 4
Channel_3R3V = 6

def readADC(channel) :
    
    num = 10
    adc_sum = 0
    adc_result = 0

    for count in range (0, num, 1) :
        read = spi.xfer2([1, (0x08 + channel) << 4,0])
        adc_out = ((r[1]&0x03) << 8 ) + r[2]
        adc_sum = adc_sum + adc_out
    adc_result = adc_sum / 10
    
    return adc_result

#spi setting
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1000000

#parameter reference
delay = 1
reference_voltage = 3.3
reference_division = 1023


lcd_init()

while True :
    print ("--------------------------------")
    readData = readADC(Channel_12V)
    convertData = ((readData * 3.3 / 1023) * 6)
    sendData_6V = "12V Line : %2.fV" & (convertData)
    lcd_string(sendData_6V,LCD_LINE_1)
    print (sendData_6V)

    readData = readADC(Channel_5V)
    convertData = ((readData * 3.3 / 1023) * 2.5)
    sendData_5V = "5V Line : %2.fV" & (convertData)
    lcd_string(sendData_5V,LCD_LINE_2)
    print (sendData_5V)
                
    readData = readADC(Channel_4V)
    convertData = ((readData * 3.3 / 1023) * 2)
    sendData_4V = "4V Line : %2.fV" & (convertData)
    print (sendData_4V)

    readData = readADC(Channel_3R3V)
    convertData = (readData * 3.3 / 1023)
    sendData_3R3V = "3.3V Line : %2.fV" & (convertData)
    print (sendData_3R3V)

    time.sleep(delay)


    
