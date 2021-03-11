import os, io
import datetime
import base64
import csv
import uuid
import json
import requests
from google.cloud import vision
from google.cloud.vision_v1 import types

# Will have to take in file name
FILE_NAME = '/home/pi/Desktop/capture.jpg'
# Path will have to change
FOLDER_PATH = os.getcwd()

## Initializing
def init():
    ## TODO: get a key unique to project (not using personal email)
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './FWDCapstone-91273bcabcdc.json'

    client = vision.ImageAnnotatorClient()

    image = types.Image()
    return client, image

## Feeding Image
def load_image():

    # Using a URL
    #image.source.image_uri = 'https://cdn-prod.medicalnewstoday.com/content/images/articles/270/270609/spinach.jpg'

    with io.open(FILE_NAME, 'rb') as image_file:
        content = image_file.read()

    processed_image = types.Image(content=content)
    return processed_image


### Label Detection
def detect_label(client, image, processed_image):

    response = client.label_detection(image=processed_image)
    #print(response.label_annotations[-1])
    print("hit y for yes, n for no")

    for label in response.label_annotations[1:]:
        print({'label': label.description, 'score': label.score})
        validation = input()
        if(validation == 'y'):
            print('yes')
            food_product_label = label
            print(label)
            break
        if(label == response.label_annotations[-1]):
            print('unsuccessful')

    return response, food_product_label


## Prep payload for database
def format_food_info(response, food_label):
    entry_date = datetime.datetime.today()

    ## Temporary expiry date table 
    expiry_date_table = {
        "Leaf vegetable": 20 #in days
    }
    expiry_date = entry_date + datetime.timedelta(days=expiry_date_table['Leaf vegetable'])

    payload = {
        "data": [{
            "id": str(uuid.uuid4()),
            "food_type": response.label_annotations[0].description,
            "food_product": food_label.description,
            "entry_date": entry_date.strftime('%Y-%m-%d'),
            "expiry_date": expiry_date.strftime('%Y-%m-%d')
        }]}

    json_object = json.dumps(payload, indent = 4)

    return payload

def store_payload(payload):

    headers = {'Content-Type': 'application/json'}

    response = requests.post("https://sheetdb.io/api/v1/1cszrsqnafe5t", headers=headers, json=payload)
    print(response.json())
    # error handle this somehow (visual queue?)

def send_image():
    client, image = init()
    processed_image = load_image()
    response, food_label = detect_label(client, image, processed_image)
    payload = format_food_info(response, food_label)
    store_payload(payload)
    print(payload)

