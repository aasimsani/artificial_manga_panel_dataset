from PIL import Image, ImageDraw
import numpy as np
import os
import concurrent
from tqdm import tqdm

from .page_object_classes import Page


def create_single_page(filename):
    page = Page()
    page.load_data(filename)

    page.render(show=False)

def render_pages(dataset_dir):
    
    filenames = [dataset_dir+filename for filename in os.listdir(dataset_dir) if filename.endswith(".json")]
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = list(tqdm(executor.map(create_single_page, filenames), total=len(filenames)))
