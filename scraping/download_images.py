import os


def download_db_illustrations():

    if not os.path.isfile("config/kaggle.json"):
        print("Please create a config folder in this directory and add your kaggle credentials")

    # Need to do this since it explicitly needs kaggle credentials even for import
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()

