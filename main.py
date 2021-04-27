from scraping.download_texts import download_and_extract_jesc
from scraping.download_fonts import get_font_links 
from preprocesing.text_dataset_format_changer import convert_jesc_to_dataframe
from preprocesing.extract_and_verify_fonts import extract_fonts, get_font_files, verify_font_files
from preprocesing.convert_images import convert_images_to_bw
from preprocesing.layout_engine.page_creator import create_single_page, render 
from preprocesing.layout_engine.page_dataset_creator import create_page_metadata
from tqdm import tqdm
import os
import pandas as pd

import time


if __name__ == '__main__':

    # Wrangling with the text dataset
    # download_and_extract_jesc()
    # convert_jesc_to_dataframe()

    # Font dataset
    # get_font_links() # Go and manually download files after this

    # Font verification
    # extract_fonts()
    # get_font_files()
    # verify_font_files()

    # Download image from Kaggle


    # Convert images
    # convert_images_to_bw()

    # Find speech bubble writeable area

    # Page creation
    
    # print("Loading files")
    # image_dir_path = "datasets/image_dataset/db_illustrations_bw/"
    # image_dir = os.listdir(image_dir_path) 
    # image_dir_len = len(image_dir)

    # text_dataset = pd.read_parquet("datasets/text_dataset/jesc_dialogues")

    # speech_bubbles_path = "datasets/speech_bubbles_dataset/files/"
    # speech_bubble_files = os.listdir(speech_bubbles_path)
    # speech_bubble_files = [speech_bubbles_path+filename for filename in speech_bubble_files]

    # font_files_path = "datasets/font_dataset/"
    # viable_font_files = []
    # with open(font_files_path+"viable_fonts.csv") as viable_fonts:

    #     for line in viable_fonts.readlines():
    #         path, viable = line.split(",")
    #         viable = bool(viable)
    #         if viable:
    #             viable_font_files.append(path)
                
    # print("Running creation of metadata")
    # dt = []
    # for i in tqdm(range(10000)):
    #     t1 = time.perf_counter()
    #     page = create_page_metadata(image_dir,
    #                                 image_dir_len,
    #                                 image_dir_path,
    #                                 viable_font_files,
    #                                 text_dataset,
    #                                 speech_bubble_files
    #                                 )
    #     # page.dump_data("./")
    #     t2 = time.perf_counter()
    #     delta = t2-t1
    #     dt.append(delta)
    #     # test_render(panels)
    # print("Average time", sum(dt)/len(dt))

    # for i in range(1):
    #     page = create_page_metadata(image_dir,
    #                                 image_dir_len,
    #                                 image_dir_path,
    #                                 viable_font_files,
    #                                 text_dataset,
    #                                 speech_bubble_files
    #                                 )
        # render(page, show=True)
    #     # test_render(panels)