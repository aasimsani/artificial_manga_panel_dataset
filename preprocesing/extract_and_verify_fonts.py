import os
import concurrent.futures
import zipfile
import time
from pathlib import Path
import shutil
from PIL import Image, ImageFont, ImageDraw
import dask.dataframe as dd
import itertools
from fontTools.ttLib import TTFont
from fontTools.unicode import Unicode
from fontTools.ttLib import TTLibError
from tqdm import tqdm
from . import config_file as cfg

font_dataset_path = "datasets/font_dataset/"
text_dataset_path = "datasets/text_dataset/"
fonts_raw_dir = font_dataset_path+"font_file_raw_downloads/"
fonts_zip_output = font_dataset_path+"fonts_zip_output/"
font_file_dir = font_dataset_path+"font_files/"
dataframe_file = text_dataset_path+"jesc_dialogues"
render_text_test_file = font_dataset_path + "render_test_text.txt"

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

def make_char_list(row):
    words = set(row.split())
    all_chars = []
    for word in words:
        chars = [char for char in word]
        all_chars += chars
    return all_chars

def create_character_test_string():
    df = dd.read_parquet(dataframe_file)
    print("Loaded DF. Now seperating word to characters")
    char_sep = df['Japanese'].apply(make_char_list, meta=("Japanese", "object")).compute()
    print("Char sep done. Starting making lists of characters")
    char_lists = char_sep.aggregate(lambda x: x.tolist())
    print("Made lists. Now aggregating them")
    agg_chars = list(itertools.chain.from_iterable(char_lists))
    print("Aggregation done. Now making a set")
    char_set = list(set(agg_chars))
    test_string = " ".join(char_set)
    print("Writing file")
    with open(render_text_test_file, "w+") as wf:
        wf.write(test_string)

def has_glyph(font, glyph):
    for table in font['cmap'].tables:
        if ord(glyph) in table.cmap.keys():
            return 1
    return 0

def verify_font_files():
    if not os.path.isfile(render_text_test_file):
        print("Character test string does exist. Generating!")
        create_character_test_string()

    test_string = "" 
    with open(render_text_test_file, "r") as test_file:
        test_string = test_file.readlines()[0]
    
    chars = test_string.split(" ")
    all_fonts = os.listdir(font_file_dir) 


    total_chars = len(chars)

    coverages = []
    print("Verifying fonts")
    for font_name in tqdm(all_fonts):
        if font_name == ".DS_Store":
            continue
        font_path = font_file_dir + font_name 
        try:
            font = TTFont(font_path)
        except TTLibError as e:
            print(font_path)

        has_glyph_list = []
        for char in chars:
            has_glyph_list.append(has_glyph(font, char))

        coverage = sum(has_glyph_list)/total_chars
        coverages.append([font_path, coverage])

    print("Writing viability to file:", font_dataset_path+"viable_fonts.csv")
    with open(font_dataset_path+"viable_fonts.csv", "w+") as viable_font_file: 
        for font in coverages:
            # Coverge %
            if font[1] > cfg.font_character_coverage:
                viable = True
            else:
                viable = False
            viable_font_file.write(font[0] + ","+str(viable)+"\n")
            

