import RPi.GPIO as GPIO
from picamera import PiCamera
from PIL import Image
from time import sleep

GPIO.setmode(GPIO.BOARD)

#Establish which button is for which
confirm = 12
cancel = 16

#Setup Camera
camera = PiCamera()

GPIO.setup(confirm, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(cancel, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def idle():
    print("Idling")
    sleep(0.1)
    end = False
    while(not end):
        if GPIO.input(confirm) == 0:
            openCamera()
        if GPIO.input(cancel) == 0:
            end = True

def openCamera():
    print("open")
    sleep(0.1)
    end = False
    camera.start_preview()
    while(not end):
        #Caputre and preview picture
        if GPIO.input(confirm) == 0:
           camera.capture('/home/pi/Desktop/capture.jpg')
           camera.stop_preview()
           end = True
           previewPicture()
        #Return to previous state
        if GPIO.input(cancel) == 0:
            camera.stop_preview()
            end = True

def previewPicture():
    print("preview")
    sleep(0.1)
    end = False
    im = Image.open('/home/pi/Desktop/capture.jpg')
    im.show()
    while (not end):
        if GPIO.input(confirm) == 0:
            end = True
        if GPIO.input(cancel) == 0:
            end = True

def main():
    idle()