from scraping.download_texts import download_and_extract_jesc
from scraping.download_fonts import get_font_links 
from preprocesing.text_dataset_format_changer import convert_jesc_to_dataframe
from preprocesing.extract_and_verify_fonts import extract_fonts, get_font_files, verify_font_files
from preprocesing.convert_images import convert_images_to_bw
from preprocesing.layout_engine.page_creator import create_single_page, test_render
from preprocesing.layout_engine.page_dataset_creator import create_page_metadata
from tqdm import tqdm

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

    # dt = []
    # for i in tqdm(range(5)):
    #     t1 = time.perf_counter()
    #     panels = create_page_metadata()
    #     t2 = time.perf_counter()
    #     delta = t2-t1
    #     dt.append(delta)
    #     test_render(panels)
    # print(sum(dt)/len(dt))
    # print("This took: ", (t2-t1))

    for i in range(1):
        panels = create_page_metadata()
        test_render(panels)