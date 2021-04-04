# Download dataset JESC from website and extract it
import requests
import os
import sys
from tqdm import tqdm
import tarfile

def download_file(url, filepath):
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        # total_length = r.headers.get('content-length')
        # total_length = int(total_length)

        # Content-Length is returned wrong
        total_length = int(223948808/1024)
        with open(filepath, 'wb') as f:
            for data in tqdm(r.iter_content(chunk_size=1024), total=total_length, unit='KB', unit_scale=False, unit_divisor=1024): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(data)

def download_and_extract_jesc():
    url = "https://nlp.stanford.edu/projects/jesc/data/raw.tar.gz"
    filepath = "datasets/raw.tar.gz"
    if os.path.isfile(filepath):
        print("File already exists")
    else:
        print("Downloading JESC text corpus")
        downloaded_file = download_file(url, filepath)
    
    
    

