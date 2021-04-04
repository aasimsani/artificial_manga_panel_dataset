import os
import concurrent.futures
import zipfile
import time
from pathlib import Path
import shutil
from PIL import Image, ImageFont, ImageDraw

fonts_raw_dir = "datasets/font_dataset/font_file_raw_downloads/"
fonts_zip_output = "datasets/font_dataset/fonts_zip_output/"
font_file_dir = "datasets/font_dataset/font_files/"

def unzip_file(paths):
    with zipfile.ZipFile(paths[0], 'r') as zip_ref:
        zip_ref.extractall(paths[1])


def extract_fonts():
    if not os.path.isdir(fonts_zip_output):
        os.mkdir(fonts_zip_output)

    files = os.listdir(fonts_raw_dir)
    files = [filename for filename in files if filename.endswith(".zip")]
    filepaths = [(fonts_raw_dir+filename, fonts_zip_output) for filename in files]

    # A fun expeirment with multiprocessing
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = executor.map(unzip_file, filepaths) 


def move_files(paths):
    shutil.move(paths[0], paths[1])

def get_font_files():
    # Get all relevant font files
    print("Finding font files")
    font_files = list(Path(fonts_zip_output).rglob("*.[tT][tT][fF]"))
    font_files += list(Path(fonts_raw_dir).rglob("*.[tT][tT][fF]"))
    font_files += list(Path(fonts_zip_output).rglob("*.[oO][tT][fF]"))
    font_files += list(Path(fonts_raw_dir).rglob("*.[oO][tT][fF]"))

    if not os.path.isdir(font_file_dir):
        os.mkdir(font_file_dir)

    font_files_and_paths = [(font_path, font_file_dir) for font_path in font_files]
    print("Moving font files")
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(move_files, font_files_and_paths)

    # Clean up the folder
    shutil.rmtree(fonts_zip_output)
    shutil.rmtree(fonts_raw_dir)

def verify_font_files():
    # for font in os.listdir(font_file_dir):
    return None

        



            

