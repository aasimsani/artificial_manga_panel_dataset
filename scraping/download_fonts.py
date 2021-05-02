import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import os

preview_page_file = "datasets/font_dataset/browse_links.txt"
font_links_file = "datasets/font_dataset/font_links.txt"
def get_browse_page_links():
    """
    Goes through pages of freejapanesefont.com and
    downloads each individual link to a font file page
    """
    root_url = "https://www.freejapanesefont.com/"
    total_pages = 23 

    links = []
    for page_num in tqdm(range(1, total_pages+1)):
        page_name = root_url + "page/" + str(page_num)

        resp = requests.get(page_name)

        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, features="html.parser")
            link_divs = soup.find_all("div", "preview")
            for div in link_divs:
                links.append(list(div.children)[1]['href'])

    with open(preview_page_file, "w+") as links_file:
        for link in links:
            links_file.write(link+"\n")

def get_font_links():
    """
    Wrapper for get_brower_page_links
    TODO: Add scraping of individual font
    file links
    """
    if not os.path.isfile(preview_page_file):
        print("Getting font preview pages")
        get_browse_page_links()
    else:
        print("Font preview pages txt exists")