from PIL import Image, ImageDraw
import numpy as np

# from .page_dataset_creator import get_leaf_panels


def create_single_page():

    # Default page size
    W = 1700
    H = 2400


    page = Image.new(size=(W,H), mode="L", color="white")
    page.show()
