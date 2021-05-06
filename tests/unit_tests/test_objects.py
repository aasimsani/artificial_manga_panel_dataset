import pytest
import json
import pandas as pd
import os

from preprocesing.layout_engine.page_object_classes import (
                                Page, Panel, SpeechBubble
                                )
from preprocesing.layout_engine.page_dataset_creator import (
                                get_base_panels, populate_panels
                                )
from preprocesing.layout_engine.helpers import get_leaf_panels

@pytest.fixture(scope="module")
def data_files():

    image_dir_path = "datasets/image_dataset/db_illustrations_bw/"
    image_dir = os.listdir(image_dir_path)

    text_dataset = pd.read_parquet("datasets/text_dataset/jesc_dialogues")

    speech_bubbles_path = "datasets/speech_bubbles_dataset/"

    speech_bubble_files = os.listdir(speech_bubbles_path+"/files/")
    speech_bubble_files = [speech_bubbles_path+"files/"+filename
                           for filename in speech_bubble_files
                           ]

    speech_bubble_tags = pd.read_csv(speech_bubbles_path +
                                     "writing_area_labels.csv")

    font_files_path = "datasets/font_dataset/"
    viable_font_files = []
    with open(font_files_path+"viable_fonts.csv") as viable_fonts:

        for line in viable_fonts.readlines():
            path, viable = line.split(",")
            viable = viable.replace("\n", "")
            if viable == "True":
                viable_font_files.append(path)

    return (image_dir,
            image_dir_path,
            viable_font_files,
            text_dataset,
            speech_bubble_files,
            speech_bubble_tags
            )


def test_page_dumping():
    """
    This tests checks whether
    the Page class can properly dump it's
    JSON file. If it can then it follows it
    should be able to load it as well.
    """
    page = Page()

    page_json = page.dump_data("./", dry=True)
    page_json = json.loads(page_json)
    keys = list(page_json.keys())

    assert "name" in keys
    assert "num_panels" in keys
    assert "page_type" in keys
    assert "page_size" in keys
    assert "background" in keys
    assert "children" in keys
    assert "speech_bubbles" in keys


def test_page_loading():
    """
        Can't test much here except for loading
        the files properly
    """    
    page = Page()
    page.load_data("tests/unit_tests/test_files/test.json")


@pytest.mark.parametrize(
    "num_panels, speech_bubbles",
    [
        (1, True),
        (2, True),
        (3, True),
        (4, True),
        (5, True),
        (6, True),
        (7, True),
        (8, True),
        (1, False),
        (2, False),
        (3, False),
        (4, False),
        (5, False),
        (6, False),
        (7, False),
        (8, False),
    ]
)
def test_page_rendering(num_panels, speech_bubbles, data_files):

    page = get_base_panels(num_panels=num_panels)

    if speech_bubbles:

        page = populate_panels(page, *data_files)

    page.render(show=False)


def test_panel_get_polygons():
    """
    This tests whether the get polygon method
    of panels works properly
    """

    page = get_base_panels(num_panels=3, layout_type="vh")

    p1 = page.get_child(0)
    p2 = page.get_child(1)

    # Returns values from x1y1 vars
    p1.non_rect = False
    p1.coords.pop()
    p1.coords.pop()

    assert len(p1.get_polygon()) == 5

    # Returns values directly from coords var
    p2.coords[0] = [None, None]
    p2.non_rect = True
    assert p2.get_polygon()[0] == [None, None]


# Speech Bubble - All paths tests
    # Dumping data
        # Keys required
    # Can render inverted bubble
    # Can render all types of transforms
    # Can render horizontal and vertical
