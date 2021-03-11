import RPi.GPIO as GPIO
from picamera import PiCamera
from PIL import Image
from time import sleep
import image_forward as vision

GPIO.setmode(GPIO.BOARD)

#Establish which button is for which
confirm = 12
cancel = 16

#Setup Camera
camera = PiCamera()
camera.resolution = (640, 480)

GPIO.setup(confirm, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(cancel, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def idle():
    print("Idling")
    sleep(0.1)
    while(True):
        if GPIO.input(confirm) == 0:
            return True
        if GPIO.input(cancel) == 0:
            return False

def openCamera():
    print("open")
    sleep(0.1)
    camera.start_preview()
    while(True):
        #Caputre and preview picture
        if GPIO.input(confirm) == 0:
           camera.capture('/home/pi/Desktop/capture.jpg')
           camera.stop_preview()
           return True
        #Return to previous state
        if GPIO.input(cancel) == 0:
            camera.stop_preview()
            return False

def previewPicture():
    print("preview")
    sleep(0.1)
    im = Image.open('/home/pi/Desktop/capture.jpg')
    while (True):
        im.show()
        if GPIO.input(confirm) == 0:
            return True
        if GPIO.input(cancel) == 0:
            return False

def main():
    state = 'idle'
    end = False
    while (not end):
        if(state == 'idle'):
            response = idle()
            if (response):
                state = 'open'
            else:
                end = True
        elif(state == 'open'):
            response = openCamera()
            if (response):
                state = 'preview'
            else:
                state = 'idle'
        elif(state == 'preview'):
            response = previewPicture()
            if(response):
                state = 'send'
            else:
                state = 'open'
        elif(state == 'send'):
            print("Sending Image...")
            vision.send_image()
            state = 'idle'