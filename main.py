from scraping.download_texts import download_and_extract_jesc
from scraping.download_fonts import get_font_links 
from preprocesing.text_dataset_format_changer import convert_jesc_to_dataframe
from preprocesing.extract_and_verify_fonts import extract_fonts, get_font_files, verify_font_files


if __name__ == '__main__':
    # download_and_extract_jesc()
    # convert_jesc_to_dataframe()
    # get_font_links()
    # extract_fonts()
    # get_font_files()
    verify_font_files()
