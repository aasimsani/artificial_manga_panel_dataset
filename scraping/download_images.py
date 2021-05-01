import os
import json

def download_db_illustrations():
    kaggle_json = "config/kaggle.json"
    if not os.path.isfile(kaggle_json):
        print("Please create a config folder in this directory and add your kaggle credentials")
        return

    # Need to do this since it explicitly needs kaggle credentials even for import
    # KAGGLE_USERNAME = ""
    # KAGGLE_KEY= ""

    # with open(kaggle_json) as json_file:
    #     data = json.loads(json_file)

    #     KAGGLE_USERNAME = data['username']
    #     KAGGLE_KEY = data['key']

    os.environ['KAGGLE_CONFIG_DIR'] = "config/" 

    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()

    dataset = "mylesoneill/tagged-anime-illustrations"
    api.dataset_download_files(dataset, path="datasets/image_dataset", quiet=False, unzip=False)

    print("Finished downloading now unzipping")
    os.system("unzip datasets/image_dataset/tagged-anime-illustrations.zip")
    print("Finished unzipping")

def download_speech_bubbles():

    pass