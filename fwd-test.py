import os, io

import datetime
import base64
import csv
import uuid
import json
import time
import requests
from google.cloud import vision
from google.cloud.vision_v1 import types

# Will have to take in file name
FILE_NAME = "grape.jpeg"
# Path will have to change
FOLDER_PATH = r'/Users/david.murga/Repos/School/fwd-capstone'

food_types = ['Fruit']

## Initializing
def init():
    ## TODO: get a key unique to project (not using personal email)
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './fwd-capstone-61889238a64c.json'

    client = vision.ImageAnnotatorClient()

    image = types.Image()
    return client, image

## Feeding Image
def load_image():

    # Using a URL
    #image.source.image_uri = 'https://cdn-prod.medicalnewstoday.com/content/images/articles/270/270609/spinach.jpg'

    with io.open(os.path.join(FOLDER_PATH, FILE_NAME), 'rb') as image_file:
        content = image_file.read()

    processed_image = types.Image(content=content)
    return processed_image


### Label Detection
def detect_label(client, image, processed_image):

    response = client.object_localization(image=processed_image)
    # response = client.label_detection(image=processed_image)
    #print(response.label_annotations[-1])
    print("hit y for yes, n for no")

    food_product_label = {}
    result = False

    #print(response.localized_object_annotations)

    for label in response.localized_object_annotations:
        if label.name not in food_types:
            print({'label': label.name, 'score': label.score})
            validation = input()
            if(validation == 'y'):
                print('yes')
                food_product_label = label
                #print(label)
                result = True
                break
            if(label == response.localized_object_annotations[-1]):
                print('unsuccessful')

    return response, food_product_label, result


def get_expiry_date(food_label):
    csv_file = csv.reader(open('expirationDates.csv', "r"), delimiter=",")
    
    #default
    min_expiry = 14
    max_expiry = 14

    for row in csv_file:
    #if current rows 2nd value is equal to input, print that row
        if food_label == row[0]:
            min_expiry = int(row[-2])
            max_expiry = int(row[-1])
    
    # TODO: need some handling if there is no entry

    return [min_expiry, max_expiry]

## Prep payload for database
def format_food_info(response, food_label):
    entry_date = datetime.datetime.today()

    expiry_date = get_expiry_date(food_label.name)
    min_expiry_date = entry_date + datetime.timedelta(expiry_date[0])
    max_expiry_date = entry_date + datetime.timedelta(expiry_date[1])

    entry_date_format = entry_date.strftime('%Y-%m-%d')
    min_expiry_date_format = min_expiry_date.strftime('%Y-%m-%d')
    max_expiry_date_format = max_expiry_date.strftime('%Y-%m-%d')



    # payload = {
    #     "data": [{
    #         "id": str(uuid.uuid4()),
    #         #"food_type": response.label_annotations[0].description,
    #         "food_product": food_label.name,
    #         "entry_date": entry_date.strftime('%Y-%m-%d'),
    #         "min_expiry_date": min_expiry_date.strftime('%Y-%m-%d'),
    #         "max_expiry_date": max_expiry_date.strftime('%Y-%m-%d')
    #     }]}

    # payload = {
    #     "data": [{
    #         "id": str(uuid.uuid4()),
    #         "food_product": food_label.name,
    #         "entry_date": entry_date_format,
    #         "min_expiry_date": min_expiry_date_format,
    #         "max_expiry_date": max_expiry_date_format
    #     }]}

    data = [{
        "id": str(uuid.uuid4()),
        "food_product": food_label.name,
        "entry_date": entry_date_format,
        "min_expiry_date": min_expiry_date_format,
        "max_expiry_date": max_expiry_date_format
        }]

    #print(payload)

    json_object = json.dumps(data, indent = 4)

    print(json_object)

    #return payload
    return json_object

def store_payload(payload):

    headers = {'Content-Type': 'application/json'}
    response = requests.post("https://sheetdb.io/api/v1/1cszrsqnafe5t", headers=headers, json=payload)
    print(response.json())
    # error handle this somehow (visual prompt?)

def main():
    client, image = init()
    processed_image = load_image()
    response, food_label, result = detect_label(client, image, processed_image)
    if (result):
        payload = format_food_info(response, food_label)
        store_payload(payload)

main()

