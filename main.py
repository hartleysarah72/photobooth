# File Name:  hartley_sarah_AS15.py
# File Path:  /home/hartleysarah/Python/hartley_sarah_AS15.py
# Run Command: sudo python3 /home/hartleysarah/Python/hartley_sarah_AS15.py

# Sarah Hartley
# 11/11/19
# AS.15
# Photobooth

# Import Libraries
import RPi.GPIO as GPIO # Raspberry Pi GPIO library
import time # Time library
from PIL import Image # PILLOW library
from picamera import PiCamera, Color # PiCamera library
from twython import Twython # Twython library


# Setup GPIO
GPIO.setwarnings(False) # Ignore warnings
GPIO.setmode(GPIO.BCM) # Use BCM Pin numbering
GPIO.setup(22, GPIO.IN)

# GPIO ports for the 8seg pins
segments =  (25,23,12,5,6,16,24,13)
# 8seg_segment_pins (14,16,13,3,5,11,15,7) +  100R inline
 
for segment in segments:
    GPIO.setup(segment, GPIO.OUT)
    GPIO.output(segment, 0)
 
# GPIO ports for the digit 0-1 pins 
digits = (17,27)
# 8seg_digit_pins (6,8) digits 0-1 respectively
 
for digit in digits:
    GPIO.setup(digit, GPIO.OUT)
    GPIO.output(digit, 1)

# Variable for decimal on display
dec = 0

# Outputs for each number
num = {' ':(0,0,0,0,0,0,0,dec),
    '0':(1,1,1,1,1,1,0,dec),
    '1':(0,1,1,0,0,0,0,dec),
    '2':(1,1,0,1,1,0,1,dec),
    '3':(1,1,1,1,0,0,1,dec),
    '4':(0,1,1,0,0,1,1,dec),
    '5':(1,0,1,1,0,1,1,dec),
    '6':(1,0,1,1,1,1,1,dec),
    '7':(1,1,1,0,0,0,0,dec),
    '8':(1,1,1,1,1,1,1,dec),
    '9':(1,1,1,1,0,1,1,dec)}


# Define functions

# Starts 5 second countdown
def countdown():
        for j in range(5):
            s = str(4-j)
            for k in range(100):
                n = str(9-k//10)
                GPIO.output(17, 0)
                global dec
                dec = 1
                for loop in range(8):
                    GPIO.output(segments[loop], num[s][loop])
                time.sleep(.005)
                GPIO.output(17, 1)
                GPIO.output(27, 0)
                dec = 0
                for loop in range(8):
                    GPIO.output(segments[loop], num[n][loop])
                time.sleep(.005)

# Takes 4 pictures at 5-second intervals
def takePictures():
    camera = PiCamera()
    camera.rotation = 180
    camera.resolution = (500, 500)

    camera.start_preview()
    for i in range(4):
        countdown()
        camera.capture("/home/hartleysarah/Pictures/Image0%s.jpg" % (i+1))
    camera.stop_preview()

# Combines 4 pictures into 1 strip
def imageStitch():
    IMAGESIZE = 500
    BORDER = 50
    NUM = 4
    LOGOWIDTH = 125
    LOGOHEIGHT = 115

    imageList = []
    for i in range(NUM):
        imageList.append(Image.open("/home/hartleysarah/Pictures/Image0" + str(i+1) +".jpg"))

    Logo = Image.open("/home/hartleysarah/Pictures/sulogo.png")
    Logo = Logo.resize((LOGOWIDTH,LOGOHEIGHT))

    newImage = Image.new("RGB", (NUM*IMAGESIZE+(NUM+1)*BORDER, IMAGESIZE+2*BORDER), (0, 0, 0) )

    for i in range(NUM):
        newImage.paste(imageList[i],((i+1)*BORDER+i*IMAGESIZE,BORDER))

    newImage.paste(Logo,(NUM*IMAGESIZE-LOGOWIDTH+NUM*BORDER,IMAGESIZE-LOGOHEIGHT+BORDER))

    newImage.save("/home/hartleysarah/Pictures/Saved.jpg")

# Posts final photo strip to Twitter @hartleyrpi
def tweet():
    # Fill in your keys and token infollowing variables 
    C_key = "removed for security" 
    C_secret = "removed for security" 
    A_token = "removed for security" 
    A_secret = "removed for security" 

    # Authenticate to your app.
    myTweet = Twython(C_key,C_secret,A_token,A_secret) 

    # Tweet Photos 
    photo = open('/home/hartleysarah/Pictures/Saved.jpg', 'rb') 
    response = myTweet.upload_media(media=photo)
    myTweet.update_status(status='Check out this cool image!', media_ids=[response['media_id']])
    
# Define Callback Function
def button_callback(channel): 
    print ("Button Falling Edge")
    global inProgress
    if not inProgress:
        print("Taking pictures!")
        inProgress = 1
        takePictures()
        imageStitch()
#       tweet()
        inProgress = 0
    else:
        print("In progress!")
    
    
# Main code
inProgress = 0  # 1 if running, 0 if not

# Add event detectors
GPIO.add_event_detect(22, GPIO.FALLING, callback=button_callback, bouncetime=300)

try:
# Setup infinite loop
    while(1): 
        time.sleep(1e6) # Sleep and wait for button detects

except KeyboardInterrupt: 
    # This code runs on a Keyboard Interrupt <CNTRL>+C
    print('\n\n' + 'Program exited on a Keyboard Interrupt' + '\n') 

except: 
    # This code runs on any error
    print('\n' + 'Errors occurred causing your program to exit' + '\n')

finally: 
    # This code runs on every exit and sets any used GPIO pins to input mode.
    GPIO.cleanup()





