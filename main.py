from scraping.download_texts import download_and_extract_jesc
from scraping.download_fonts import get_font_links 
from preprocesing.text_dataset_format_changer import convert_jesc_to_dataframe
from preprocesing.extract_and_verify_fonts import extract_fonts, get_font_files, verify_font_files
from preprocesing.convert_images import convert_images_to_bw
from preprocesing.layout_engine.page_creator import create_single_page, render 
from preprocesing.layout_engine.page_dataset_creator import create_page_metadata
from tqdm import tqdm
import os

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
    # convert_images_to_bw()

    # Page creation
    # create_single_page()

    dt = []

    image_dir_path = "datasets/image_dataset/db_illustrations_bw/"
    image_dir = os.listdir(image_dir_path) 
    image_dir_len = len(image_dir)
    # for i in tqdm(range(10000)):
    #     t1 = time.perf_counter()
    #     panels = create_page_metadata(image_dir, image_dir_len, image_dir_path)
    #     t2 = time.perf_counter()
    #     delta = t2-t1
    #     dt.append(delta)
    #     # test_render(panels)
    # print("Average time", sum(dt)/len(dt))

    for i in range(1):
        page = create_page_metadata(image_dir, image_dir_len, image_dir_path)
        page.dump_data("./")
        render(page, show=True)
        # test_render(panels)