from scraping.download_texts import download_and_extract_jesc
from scraping.download_fonts import get_font_links 
from scraping.download_images import download_db_illustrations

from preprocesing.text_dataset_format_changer import convert_jesc_to_dataframe
from preprocesing.extract_and_verify_fonts import extract_fonts, get_font_files, verify_font_files
from preprocesing.convert_images import convert_images_to_bw
from preprocesing.layout_engine.page_creator import render_pages 
from preprocesing.layout_engine.page_dataset_creator import create_page_metadata

from tqdm import tqdm
import os
import pandas as pd
from argparse import ArgumentParser

import time

if __name__ == '__main__':

    usage_message = """
                    This file is designed you to create the AMP dataset
                    To learn more about how to use this open the README.md
                    """

    parser = ArgumentParser(usage=usage_message)

    parser.add_argument("--download_jesc", "-dj", action="store_true",
                        help="Download JESC Japanese/English dialogue corpus")
    parser.add_argument("--download_fonts", "-df", action="store_true",
                        help="Scrape font files")
    parser.add_argument("--download_images", "-di", action="store_true",
                        help="Download anime illustrtations from Kaggle")
    parser.add_argument("--download_speech_bubbles", "-ds", action="store_true",
                         help="Download speech bubbles from Gcloud")

    parser.add_argument("--verify_fonts", "-vf", action="store_true",
                        help="Verify fonts for minimum coverage from")

    parser.add_argument("--create-page-metadata", "-pm", nargs=1, type=int)
    parser.add_argument("--render_pages", "-rp", action="store_true")
    parser.add_argument("--generate_pages", "-gp", nargs=1, type=int)

    args = parser.parse_args()

    # Wrangling with the text dataset
    if args.download_jesc:
        download_and_extract_jesc()
        convert_jesc_to_dataframe()

    # Font dataset
    # TODO: Add an automatic scraper
    if args.download_fonts: 
        get_font_links() 
        print("Please run scraping/font_download_manual.ipynb"+ 
                 " and download fonts manually from the links that were scraped"+
                 "then place them in datasets/font_dataset/font_file_raw_downloads/")
        print("NOTE: There's no need to extract them this program takes care of that")

    # Font verification
    if args.verify_fonts:
        # extract_fonts()
        verify_font_files()

    # Download and convert image from Kaggle
    if args.download_images:
        download_db_illustrations()
        convert_images_to_bw()

    # Page creation
    if args.create_page_metadata is not None:
        metadata_folder = "datasets/page_metadata/"
        if not os.path.isdir(metadata_folder):
            os.mkdir(metadata_folder)

        # number of pages
        n = args.create_page_metadata[0]
        print("Loading files")
        image_dir_path = "datasets/image_dataset/db_illustrations_bw/"
        image_dir = os.listdir(image_dir_path) 

        text_dataset = pd.read_parquet("datasets/text_dataset/jesc_dialogues")

        speech_bubbles_path = "datasets/speech_bubbles_dataset/"

        speech_bubble_files = os.listdir(speech_bubbles_path+"/files/")
        speech_bubble_files = [speech_bubbles_path+"files/"+filename for filename in speech_bubble_files]
        speech_bubble_tags = pd.read_csv(speech_bubbles_path+"writing_area_labels.csv")
        font_files_path = "datasets/font_dataset/"
        viable_font_files = []
        with open(font_files_path+"viable_fonts.csv") as viable_fonts:

            for line in viable_fonts.readlines():
                path, viable = line.split(",")
                viable = viable.replace("\n", "")
                if viable == "True":
                    viable_font_files.append(path)

        print("Running creation of metadata")
        for i in tqdm(range(n)):
            page = create_page_metadata(image_dir,
                                        image_dir_path,
                                        viable_font_files,
                                        text_dataset,
                                        speech_bubble_files,
                                        speech_bubble_tags
                                        )
            page.dump_data(metadata_folder, dry=False)

    if args.render_pages:

        metadata_folder = "datasets/page_metadata/"
        images_folder = "datasets/page_images/"
        if not os.path.isdir(metadata_folder):
            print("There is no metadata please generate metadata first")
        else:        
            if not os.path.isdir(images_folder):
                os.mkdir(images_folder)

            print("Loading metadata and rendering")
            render_pages(metadata_folder, images_folder)

    # Combines the above in case of small size
    if args.generate_pages is not None:
        # number of pages
        n = args.generate_pages[0]

        metadata_folder = "datasets/page_metadata/"
        if not os.path.isdir(metadata_folder):
            os.mkdir(metadata_folder)

        print("Loading files")
        image_dir_path = "datasets/image_dataset/db_illustrations_bw/"
        image_dir = os.listdir(image_dir_path) 

        text_dataset = pd.read_parquet("datasets/text_dataset/jesc_dialogues")

        speech_bubbles_path = "datasets/speech_bubbles_dataset/"

        speech_bubble_files = os.listdir(speech_bubbles_path+"/files/")
        speech_bubble_files = [speech_bubbles_path+"files/"+filename for filename in speech_bubble_files]
        speech_bubble_tags = pd.read_csv(speech_bubbles_path+"writing_area_labels.csv")
        font_files_path = "datasets/font_dataset/"
        viable_font_files = []
        with open(font_files_path+"viable_fonts.csv") as viable_fonts:

            for line in viable_fonts.readlines():
                path, viable = line.split(",")
                viable = viable.replace("\n", "")
                if viable == "True":
                    viable_font_files.append(path)

        print("Running creation of metadata")
        for i in tqdm(range(n)):
            page = create_page_metadata(image_dir,
                                        image_dir_path,
                                        viable_font_files,
                                        text_dataset,
                                        speech_bubble_files,
                                        speech_bubble_tags
                                        )
            page.dump_data(metadata_folder, dry=False)
        
        if not os.path.isdir(metadata_folder):
            print("There is no metadata please generate metadata first")
        else: 
            images_folder = "datasets/page_images/"
            if not os.path.isdir(images_folder):
                os.mkdir(images_folder)

            print("Loading metadata and rendering")
            render_pages(metadata_folder, images_folder)