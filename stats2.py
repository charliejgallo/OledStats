'''
	OLEDStats

2019, charliejgallo

starting with the example from: https://learn.adafruit.com/adafruit-pioled-128x32-mini-oled-for-raspberry-pi/usage

required: 

	sudo pip3 install adafruit-circuitpython-ssd1306
	sudo apt-get install python3-pil

Added to adafruit's example:
	- Oled changed from 128x32 to 128x64
	- CPU temperature
	- CPU Frequency
	- Intro screen
	- Atexit/sigterm

Launch Script on Startup:
	-sudo nano /etc/rc.local 				(raspberry pi)
 	-add "sudo python3 /home/pi/OledStats/stats2.py &"(change location if needed) before the "exit 0" line 


'''


# Copyright (c) 2017 Adafruit Industries
# Author: Tony DiCola & James DeVito
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


# This example is for use on (Linux) computers that are using CPython with
# Adafruit Blinka to support CircuitPython libraries. CircuitPython does
# not support PIL/pillow (python imaging library)!

import time
import subprocess
import atexit
import signal

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306


# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)

# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these
# to the right size for your display!
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

# Clear display.
disp.fill(0)
disp.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = 0
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Load default font.
#font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 9)
font2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)

#at exit or shutdown:
def exit_handler():
	print ("Closing Oled Stats!!")
	draw.rectangle((0, 0, width, height), outline=0, fill=0)
	disp.image(image)
	disp.show()

#check for exit signal	
atexit.register(exit_handler)				

##Intro Screen
draw.rectangle((0, 0, width, height), outline=0, fill=0)
draw.text((12, top+12), "PI4Coral", font=font2, fill=255)
draw.text((44, top+52), " by charliejgallo", font=font, fill=255)
disp.image(image)
disp.show()
time.sleep(4)

#Loop:
while True:
	
    # Draw a black filled box to clear the image.
	draw.rectangle((0, 0, width, height), outline=0, fill=0)

	# Shell scripts for system monitoring from here:
	# https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
	# IP Address
	cmd = "hostname -I | cut -d\' \' -f1"
	IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
	# CPU load
	cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
	CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
	# RAM usage
	cmd = "free -m | awk 'NR==2{printf \"RAM: %s/%s MB %.2f%%\", $3,$2,$3*100/$2 }'"
	MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
	# DISK usage
	cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%d GB %s\", $3,$2,$5}'"
	Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")
	# CPU temp
	tFile = open('/sys/class/thermal/thermal_zone0/temp')
	temp = float(tFile.read())
	tempC = temp/1000
	tempC = round(tempC,2)
	# CPU freq
	tFile2 = open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq')
	freq = float(tFile2.read())
	Freq = freq/1000
	Freq = round(Freq,0)
	
   	# Write the six lines of text.
	draw.text((x, top+1), "CPU Temp: "+str(tempC)+" C", font=font, fill=255)
	draw.text((x, top+10), CPU, font=font, fill=255)
	draw.text((x, top+19), "CPU Freq: "+str(Freq)+" MHZ", font=font, fill=255)
	draw.text((x, top+28), "IP: "+IP, font=font, fill=255)
	draw.text((x, top+37), MemUsage, font=font, fill=255)
	draw.text((x, top+46), Disk, font=font, fill=255)
	
	# Display image.
	disp.image(image)
	disp.show()
	signal.signal(signal.SIGTERM, exit_handler)		#check for shutdown signal
	time.sleep(1)									# refresh 1 time per second


