import pytest
from preprocesing.layout_engine.page_dataset_creator import (
    draw_n_shifted,
    draw_n,
    draw_two_shifted
)
from preprocesing.layout_engine.page_object_classes import Panel, Page
import numpy as np
from preprocesing import config_file as cfg


@pytest.mark.parametrize(
    "n, horizontal_vertical",
    [
        (2, "h"),
        (3, "h"),
        (4, "h"),
        (5, "h"),
        (6, "h"),
        (7, "h"),
        (8, "h"),
        (2, "v"),
        (3, "v"),
        (4, "v"),
        (5, "v"),
        (6, "v"),
        (7, "v"),
        (8, "v"),
    ]
)
def test_draw_n_shifted(n, horizontal_vertical):
    """
    Test whether the draw_n_shfited function can:
    - Add children from 1 to 8
    - Do so horizontally and vertically
    - Check if the children exist at the correct
    locations

    :param n: Number of panels to create a page of

    :type n: int

    :param horizontal_vertical: Whether to render
    the panels horizontally or vertically

    :type horizontal_vertical: str
    """

    page = Page()
    assert len(page.children) == 0

    # Allow each inital panel to grow to up to 150% of 100/n
    # which would be all panel's equal.
    # This is then normalized down to a smaller number
    choice_max = round((100/n)*1.5)
    choice_min = round((100/n)*0.5)

    normalized_shifts = []

    # If there are no ratios specified
    shifts = []
    for i in range(0, n):
        # Randomly select a size for the new panel's side
        shift_choice = np.random.randint(choice_min, choice_max)
        # Change the maximum range acoording to available length
        # of the parent panel's size
        choice_max = choice_max + ((100/n) - shift_choice)

        # Append the shift
        shifts.append(shift_choice)

    # Amount of length to add or remove
    to_add_or_remove = (100 - sum(shifts))/len(shifts)

    # Normalize panels such that the shifts all sum to 1.0
    for shift in shifts:
        new_shift = shift + to_add_or_remove
        normalized_shifts.append(new_shift/100)

    # Start the drawing
    draw_n_shifted(n, page, horizontal_vertical, shifts=normalized_shifts)

    # Check if the correct number of children were drawn
    assert len(page.children) == n

    # Check if each child is at the correct location
    if horizontal_vertical == "h":
        shift_level = 0.0
        for i in range(n):

            child_panel = page.get_child(i)
            topleft = child_panel.x1y1
            topright = child_panel.x2y2
            if i == 0:
                assert topleft[1] == 0.0
                assert topright[1] == 0.0
            else:
                shift_level += normalized_shifts[i-1]
                assert topleft[1] == cfg.page_height*shift_level
                assert topright[1] == cfg.page_height*shift_level
    else:
        shift_level = 0.0
        for i in range(n):

            child_panel = page.get_child(i)
            topleft = child_panel.x1y1
            bottomleft = child_panel.x4y4
            if i == 0:
                assert topleft[0] == 0.0
                assert bottomleft[0] == 0.0
            else:
                shift_level += normalized_shifts[i-1]
                assert topleft[0] == cfg.page_width*shift_level
                assert bottomleft[0] == cfg.page_width*shift_level


@pytest.mark.parametrize(
    "n, horizontal_vertical",
    [
        (2, "h"),
        (3, "h"),
        (4, "h"),
        (5, "h"),
        (6, "h"),
        (7, "h"),
        (8, "h"),
        (2, "v"),
        (3, "v"),
        (4, "v"),
        (5, "v"),
        (6, "v"),
        (7, "v"),
        (8, "v"),
    ]
)
def test_draw_n(n, horizontal_vertical):
    """
    Test whether the draw_n function can:
    - Add children from 1 to 8
    - Do so horizontally and vertically
    - Check if the children exist at the correct
    locations

    :param n: Number of panels to create a page of

    :type n: int

    :param horizontal_vertical: Whether to render
    the panels horizontally or vertically

    :type horizontal_vertical: str
    """

    page = Page()
    assert len(page.children) == 0

    # Start the drawing
    draw_n(n, page, horizontal_vertical)

    # Check if the correct number of children were drawn
    assert len(page.children) == n

    # Check if each child is at the correct location
    if horizontal_vertical == "h":
        for i in range(n):

            child_panel = page.get_child(i)
            # Get the top left to check whether it's y value
            # has been shifted properly to create horziontal
            # randomly shifted panels
            topleft = child_panel.x1y1
            topright = child_panel.x2y2
            if i == 0:
                assert topleft[1] == 0.0
                assert topright[1] == 0.0
            else:
                assert topleft[1] == cfg.page_height*(i/n)
                assert topright[1] == cfg.page_height*(i/n)

    else:
        shift_level = 0.0
        for i in range(n):

            child_panel = page.get_child(i)
            # Get the top left to check whether it's x value
            # has been shifted properly to create vertically
            # randomly shifted panels
            topleft = child_panel.x1y1
            bottomleft = child_panel.x4y4
            if i == 0:
                assert topleft[0] == 0.0
                assert bottomleft[0] == 0.0
            else:
                assert topleft[0] == cfg.page_width*(i/n)
                assert bottomleft[0] == cfg.page_width*(i/n)


@pytest.mark.parametrize(
    "horizontal_vertical",
    [
        "h",
        "v"
    ]
)
def test_draw_two_shifted(horizontal_vertical):
    """
    Test whether the draw_two_shfited function can:
    - Add two children
    - Do so horizontally and vertically
    - Check if the children exist at the correct
    locations

    :param horizontal_vertical: Whether to render
    the panels horizontally or vertically

    :type horizontal_vertical: str
    """

    page = Page()
    assert len(page.children) == 0

    # Manually generate a shift for verification
    shift_min = 25
    shift_max = 75
    shift = np.random.randint(shift_min, shift_max)
    shift = shift/100

    # Start the drawing
    draw_two_shifted(page, horizontal_vertical, shift=shift)

    # Check if the child is at the correct spot
    child_0 = page.get_child(0)
    child_1 = page.get_child(1)

    if horizontal_vertical == "h":

        bottomleft_0 = child_0.x4y4
        topleft_1 = child_1.x1y1

        bottomright_0 = child_0.x3y3
        topright_1 = child_1.x2y2

        # Get Y coords which change in the horzontal split
        assert bottomleft_0[1] == cfg.page_height*shift
        assert bottomright_0[1] == cfg.page_height*shift

        # Make sure panels are sharing boundaries
        assert bottomleft_0[1] == topleft_1[1]
        assert bottomright_0[1] == topright_1[1]

    else:

        topright_0 = child_0.x2y2
        topleft_1 = child_1.x1y1

        bottomright_0 = child_0.x3y3
        bottomleft_1 = child_1.x4y4

        # Get Y coords which change in the horzontal split
        assert topright_0[0] == cfg.page_width*shift
        assert bottomright_0[0] == cfg.page_width*shift

        # Make sure panels are sharing boundaries
        assert topright_0[0] == topleft_1[0]
        assert bottomright_0[0] == bottomleft_1[0]


# Single slice panels
    # H and V paths
    # Provide page with 1 panel see if it
    # slices them into two
    # If more than one test if at least 1
    # panel got sliced if it's the correct area
# Box transform panels
    # Provide a page with only 1 set of 3 panels
    # Test if it get's moved to be a rhombus and a trapezoid
# Box transform page
    # H and V paths
    # Check if the children actually move
    # Check explcit type choicing
# Shrink Panels
    # Check reduction in area of panels
# Remove Panels
    # Check if there are less panels
# Add background
    # Check if background was added to Panel and Page
# Create single panel meta
    # Test calculation of bubble
    # location
# Get base panels
    # Test for num pages
    # Orientation
    # 1 and greater edge cases
    # Each layout hiearchy
