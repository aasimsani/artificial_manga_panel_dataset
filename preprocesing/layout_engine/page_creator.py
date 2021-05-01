from PIL import Image, ImageDraw
import numpy as np
import os
import concurrent
from tqdm import tqdm

from .page_object_classes import Page
from .. import config_file as cfg


def create_single_page(paths):
    """
    This function is used to render a single page from a metadata json file
    to a target location.

    :param paths:  a tuple of the page metadata and output path
    :type tuple
    """
    metadata = paths[0]
    images_path = paths[1]

    page = Page()
    page.load_data(metadata)
    filename = images_path+page.name+cfg.output_format
    if not os.path.isfile(filename):

        img = page.render(show=False)
        img.save(filename)


def render_pages(metadata_dir, images_dir):
    """
    Takes metadata json files and renders page images

    :param metadata_dir: A directory containing all the metadata json files
    :type str:
    :param images_dir: The output directory for the rendered pages
    """
    
    filenames = [(metadata_dir+filename, images_dir)for filename in os.listdir(metadata_dir) if filename.endswith(".json")]
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = list(tqdm(executor.map(create_single_page, filenames), total=len(filenames)))
