from PIL import Image, ImageDraw
import numpy as np
import os
import concurrent
from tqdm import tqdm

from .page_object_classes import Page
from .. import config_file as cfg


def create_single_page(data):
    """
    This function is used to render a single page from a metadata json file
    to a target location.

    :param paths:  a tuple of the page metadata and output path
    as well as whether or not to save the rendered file i.e. dry run or
    wet run

    :type paths: tuple
    """
    metadata = data[0]
    images_path = data[1]
    dry = data[2]

    page = Page()
    page.load_data(metadata)
    filename = images_path+page.name+cfg.output_format
    if not os.path.isfile(filename) and not dry:

        img = page.render(show=False)
        img.save(filename)


def render_pages(metadata_dir, images_dir, dry=False):
    """
    Takes metadata json files and renders page images

    :param metadata_dir: A directory containing all the metadata json files

    :type metadata_dir: str

    :param images_dir: The output directory for the rendered pages

    :type images_dir: str
    """

    filenames = [(metadata_dir+filename, images_dir, dry)
                 for filename in os.listdir(metadata_dir)
                 if filename.endswith(".json")]

    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = list(tqdm(executor.map(create_single_page, filenames),
                            total=len(filenames)))
