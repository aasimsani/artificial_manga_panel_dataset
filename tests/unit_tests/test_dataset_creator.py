import pytest
import numpy as np
from copy import deepcopy
from preprocesing.layout_engine.page_dataset_creator import (
    draw_n_shifted,
    draw_n,
    draw_two_shifted,
    single_slice_panels,
    box_transform_panels,
    box_transform_page,
    get_base_panels
)
from preprocesing.layout_engine.helpers import invert_for_next, get_leaf_panels
from preprocesing.layout_engine.page_object_classes import Panel, Page
# from preprocesing import config_file as cfg


@pytest.fixture
def make_panel():
    """
    Makes panels/pages for testing

    :return: Based on the type of panel
    requested a tuple of a Page, Panel
    or None, Page

    :rtype: tuple
    """

    def _make_panel(panel_type, horizontal_vertical):
        page = Page()
        if panel_type == "page":
            return None, page
        else:

            large_coords = [
                (925, 0),
                (1700, 0),
                (1700, 2400),
                (925, 2400)
            ]
            panel_large = Panel(coords=large_coords,
                                name="large",
                                parent=page,
                                orientation=horizontal_vertical
                                )

            page.add_child(panel_large)

            if panel_type == "large":

                return page, panel_large

            elif panel_type == "small":
                small_coords = [
                    (925, 800),
                    (1700, 800),
                    (1700, 2400),
                    (925, 2400)
                ]

                panel_small = Panel(coords=small_coords,
                                    name="small",
                                    parent=panel_large,
                                    orientation=horizontal_vertical
                                    )

                panel_large.add_child(panel_small)

                return page, panel_small

    return _make_panel


@pytest.mark.parametrize(
    "n, horizontal_vertical, panel_type",
    [
        (2, "h", "page",),
        (3, "h", "page"),
        (4, "h", "page"),
        (5, "h", "page"),
        (6, "h", "page"),
        (7, "h", "page"),
        (8, "h", "page"),
        (2, "v", "page"),
        (3, "v", "page"),
        (4, "v", "page"),
        (5, "v", "page"),
        (6, "v", "page"),
        (7, "v", "page"),
        (8, "v", "page"),
        (2, "h", "small"),
        (3, "h", "small"),
        (4, "h", "small"),
        (5, "h", "small"),
        (6, "h", "small"),
        (7, "h", "small"),
        (8, "h", "small"),
        (2, "v", "small"),
        (3, "v", "small"),
        (4, "v", "small"),
        (5, "v", "small"),
        (6, "v", "small"),
        (7, "v", "small"),
        (8, "v", "small"),
        (2, "h", "large"),
        (3, "h", "large"),
        (4, "h", "large"),
        (5, "h", "large"),
        (6, "h", "large"),
        (7, "h", "large"),
        (8, "h", "large"),
        (2, "v", "large"),
        (3, "v", "large"),
        (4, "v", "large"),
        (5, "v", "large"),
        (6, "v", "large"),
        (7, "v", "large"),
        (8, "v", "large"),



    ]
)
def test_draw_n_shifted(n, horizontal_vertical, panel_type, make_panel):
    """
    Test whether the draw_n_shfited function can:
    - Add children from 1 to 8
    - Do so horizontally and vertically
    - Check if the children exist at the correct
    locations

    :param n: Number of panels to create

    :type n: int

    :param horizontal_vertical: Whether to render
    the panels horizontally or vertically

    :type horizontal_vertical: str

    :param panel_type: Whether we are dividing small, large or Page type
    panels

    :type panel_type: str

    :param make_panel: A function that outputs the desired panel type

    :type make_panel: function
    """

    # Panels should always slice in perpendicular
    prev_div = invert_for_next(horizontal_vertical)
    _, panel = make_panel(panel_type, prev_div)
    assert len(panel.children) == 0

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
    draw_n_shifted(n, panel, horizontal_vertical, shifts=normalized_shifts)

    # Check if the correct number of children were drawn
    assert len(panel.children) == n

    # Check if each child is at the correct location
    if horizontal_vertical == "h":
        shift_level = 0.0
        for i in range(n):

            child_panel = panel.get_child(i)
            topleft = child_panel.x1y1
            topright = child_panel.x2y2
            if i == 0:
                assert topleft[1] == panel.x1y1[1]
                assert topright[1] == panel.x2y2[1]
            else:
                shift_level += normalized_shifts[i-1]
                # Whether the panel was shifted to the correct height i.e.
                # parent panel y + shift height == dividing point for panel
                assert topleft[1] == panel.x1y1[1] + panel.height*shift_level
                assert topright[1] == panel.x1y1[1] + panel.height*shift_level
    else:
        shift_level = 0.0
        for i in range(n):

            child_panel = panel.get_child(i)
            topleft = child_panel.x1y1
            bottomleft = child_panel.x4y4
            if i == 0:
                assert topleft[0] == panel.x1y1[0]
                assert bottomleft[0] == panel.x4y4[0]
            else:
                shift_level += normalized_shifts[i-1]
                # Whether the panel was shifted to the correct height i.e.
                # parent panel x + shift height == dividing point for panel
                assert topleft[0] == panel.x1y1[0] + panel.width*shift_level
                assert bottomleft[0] == panel.x1y1[0] + panel.width*shift_level


@pytest.mark.parametrize(
    "n, horizontal_vertical, panel_type",
    [
        (2, "h", "page",),
        (3, "h", "page"),
        (4, "h", "page"),
        (5, "h", "page"),
        (6, "h", "page"),
        (7, "h", "page"),
        (8, "h", "page"),
        (2, "v", "page"),
        (3, "v", "page"),
        (4, "v", "page"),
        (5, "v", "page"),
        (6, "v", "page"),
        (7, "v", "page"),
        (8, "v", "page"),
        (2, "h", "small"),
        (3, "h", "small"),
        (4, "h", "small"),
        (5, "h", "small"),
        (6, "h", "small"),
        (7, "h", "small"),
        (8, "h", "small"),
        (2, "v", "small"),
        (3, "v", "small"),
        (4, "v", "small"),
        (5, "v", "small"),
        (6, "v", "small"),
        (7, "v", "small"),
        (8, "v", "small"),
        (2, "h", "large"),
        (3, "h", "large"),
        (4, "h", "large"),
        (5, "h", "large"),
        (6, "h", "large"),
        (7, "h", "large"),
        (8, "h", "large"),
        (2, "v", "large"),
        (3, "v", "large"),
        (4, "v", "large"),
        (5, "v", "large"),
        (6, "v", "large"),
        (7, "v", "large"),
        (8, "v", "large"),
    ]
)
def test_draw_n(n, horizontal_vertical, panel_type, make_panel):
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

    :param panel_type: Whether we are dividing small, large or Page type
    panels

    :type panel_type: str

    :param make_panel: A function that outputs the desired panel type

    :type make_panel: function
    """

    # Panels should always slice in perpendicular
    prev_div = invert_for_next(horizontal_vertical)
    _, panel = make_panel(panel_type, prev_div)
    assert len(panel.children) == 0

    # Start the drawing
    draw_n(n, panel, horizontal_vertical)

    # Check if the correct number of children were drawn
    assert len(panel.children) == n

    # Check if each child is at the correct location
    if horizontal_vertical == "h":
        for i in range(n):

            child_panel = panel.get_child(i)
            # Get the top left to check whether it's y value
            # has been shifted properly to create horziontal
            # randomly shifted panels
            topleft = child_panel.x1y1
            topright = child_panel.x2y2
            if i == 0:
                assert topleft[1] == panel.x1y1[1]
                assert topright[1] == panel.x2y2[1]
            else:
                # Whether the panel was shifted to the correct height i.e.
                # parent panel y + shift height == dividing point for panel
                assert topleft[1] == panel.x1y1[1] + panel.height*(i/n)
                assert topright[1] == panel.x1y1[1] + panel.height*(i/n)

    else:
        shift_level = 0.0
        for i in range(n):

            child_panel = panel.get_child(i)
            # Get the top left to check whether it's x value
            # has been shifted properly to create vertically
            # randomly shifted panels
            topleft = child_panel.x1y1
            bottomleft = child_panel.x4y4
            if i == 0:
                assert topleft[0] == panel.x1y1[0]
                assert bottomleft[0] == panel.x4y4[0]
            else:
                # Whether the panel was shifted to the correct height i.e.
                # parent panel x + shift height == dividing point for panel
                assert topleft[0] == panel.x1y1[0] + panel.width*(i/n)
                assert bottomleft[0] == panel.x1y1[0] + panel.width*(i/n)


@pytest.mark.parametrize(
    "horizontal_vertical, panel_type",
    [
        ("h", "page"),
        ("v", "page"),
        ("h", "large"),
        ("v", "large"),
        ("h", "small"),
        ("v", "small"),
    ]
)
def test_draw_two_shifted(horizontal_vertical, panel_type, make_panel):
    """
    Test whether the draw_two_shfited function can:
    - Add two children
    - Do so horizontally and vertically
    - Check if the children exist at the correct
    locations

    :param horizontal_vertical: Whether to render
    the panels horizontally or vertically

    :type horizontal_vertical: str

    :param panel_type: Whether we are dividing small, large or Page type
    panels

    :type panel_type: str

    :param make_panel: A function that outputs the desired panel type

    :type make_panel: function
    """

    # Panels should always slice in perpendicular
    prev_div = invert_for_next(horizontal_vertical)
    _, panel = make_panel(panel_type, prev_div)

    assert len(panel.children) == 0

    # Manually generate a shift for verification
    shift_min = 25
    shift_max = 75
    shift = np.random.randint(shift_min, shift_max)
    shift = shift/100

    # Start the drawing
    draw_two_shifted(panel, horizontal_vertical, shift=shift)

    # Check if the child is at the correct spot
    child_0 = panel.get_child(0)
    child_1 = panel.get_child(1)

    if horizontal_vertical == "h":

        bottomleft_0 = child_0.x4y4
        topleft_1 = child_1.x1y1

        bottomright_0 = child_0.x3y3
        topright_1 = child_1.x2y2

        # Get Y coords which change in the horzontal split
        assert bottomleft_0[1] == panel.x1y1[1] + panel.height*shift
        assert bottomright_0[1] == panel.x1y1[1] + panel.height*shift

        # Make sure panels are sharing boundaries
        assert bottomleft_0[1] == topleft_1[1]
        assert bottomright_0[1] == topright_1[1]

    else:

        topright_0 = child_0.x2y2
        topleft_1 = child_1.x1y1

        bottomright_0 = child_0.x3y3
        bottomleft_1 = child_1.x4y4

        # Get Y coords which change in the horzontal split
        assert topright_0[0] == panel.x1y1[0] + panel.width*shift
        assert bottomright_0[0] == panel.x1y1[0] + panel.width*shift

        # Make sure panels are sharing boundaries
        assert topright_0[0] == topleft_1[0]
        assert bottomright_0[0] == bottomleft_1[0]


@pytest.mark.parametrize(
    "horizontal_vertical, slice_type, slice_skew, panel_type",
    [
        ("h", "center", "up", "page"),
        ("h", "center", "down", "page"),
        ("v", "center", "left", "page"),
        ("v", "center", "right", "page"),
        ("h", "center", "up", "small"),
        ("h", "center", "down", "small"),
        ("v", "center", "left", "small"),
        ("v", "center", "right", "small"),
        ("h", "center", "up", "large"),
        ("h", "center", "down", "large"),
        ("v", "center", "left", "large"),
        ("v", "center", "right", "large"),
        ("h", "side", "tr", "page"),
        ("h", "side", "tl", "page"),
        ("h", "side", "br", "page"),
        ("h", "side", "bl", "page"),
        ("h", "side", "tr", "small"),
        ("h", "side", "tl", "small"),
        ("h", "side", "br", "small"),
        ("h", "side", "bl", "small"),
        ("h", "side", "tr", "large"),
        ("h", "side", "tl", "large"),
        ("h", "side", "br", "large"),
        ("h", "side", "bl", "large"),
    ]
)
def test_single_slice_panels(horizontal_vertical,
                             slice_type,
                             slice_skew,
                             panel_type,
                             make_panel
                             ):
    """
    This function tests whether the single_slice_panels
    function can:
    - Slice horzontally and vertically
    - Slice down the center and the sides
    - If slicing then the skew is to the correct side based on the type

    :param horizontal_vertical:  Whether the slice should be horizontal
    or vertical

    :type horizontal_vertical: str

    :param slice_type: Specify whether the panel should be
    sliced down the center or on a side

    :type slice_type: str

    :param slice_skew: Based on the type of slicing which direction should
    it be sliced

    :type slice_skew: str

    :param make_panel: A function that outputs the desired panel type

    :type make_panel: function
    """
    # Panels should always slice in perpendicular
    prev_div = invert_for_next(horizontal_vertical)
    page, panel = make_panel(panel_type, prev_div)

    if page is None:
        page = panel

    # Slice the panels
    page = single_slice_panels(page,
                               horizontal_vertical,
                               slice_type,
                               slice_skew,
                               number_to_slice=1
                               )
    # Make sure wrong configuration wasn't given
    assert page is not None

    panel_center_x = panel.x1y1[0] + (panel.width/2)
    panel_center_y = panel.x1y1[1] + (panel.height/2)

    panel_one_fourth_x = panel.x1y1[0] + (panel.width/4)
    panel_one_fourth_y = panel.x1y1[1] + (panel.height/4)

    panel_three_fourths_x = panel.x1y1[0] + ((3*panel.width)/4)
    panel_three_fourths_y = panel.x1y1[1] + ((3*panel.height)/4)

    p1 = panel.get_child(0)
    p2 = panel.get_child(1)

    if slice_type == "center":
        if horizontal_vertical == "v":
            # Make sure that the lines moved correctly
            # and panels share boundaries
            if slice_skew == "left":
                assert p1.x2y2[0] < panel_center_x
                assert p1.x3y3[0] > panel_center_x

                assert p2.x1y1[0] == p1.x2y2[0]
                assert p2.x4y4[0] == p1.x3y3[0]
            else:
                assert p1.x2y2[0] > panel_center_x
                assert p1.x3y3[0] < panel_center_x

                assert p2.x1y1 == p1.x2y2
                assert p2.x4y4 == p1.x3y3
        else:
            if slice_skew == "up":
                assert p1.x3y3[1] > panel_center_y
                assert p1.x4y4[1] < panel_center_y

                assert p2.x1y1[1] == p1.x4y4[1]
                assert p2.x2y2[1] == p1.x3y3[1]
            else:
                assert p1.x3y3[1] < panel_center_y
                assert p1.x4y4[1] > panel_center_y

                assert p2.x1y1[1] == p1.x4y4[1]
                assert p2.x2y2[1] == p1.x3y3[1]

    else:
        if slice_skew == "bl":
            assert p1.coords[0][1] <= panel_three_fourths_y
            assert p1.coords[0][1] >= panel_one_fourth_y

            assert p1.coords[1][0] <= panel_three_fourths_x
            assert p1.coords[1][0] >= panel_one_fourth_x

        elif slice_skew == "br":
            assert p1.coords[0][1] <= panel_three_fourths_y
            assert p1.coords[0][1] >= panel_one_fourth_y

            assert p1.coords[2][0] <= panel_three_fourths_x
            assert p1.coords[2][0] >= panel_one_fourth_x

        elif slice_skew == "tl":

            assert p1.coords[1][0] <= panel_three_fourths_x
            assert p1.coords[1][0] >= panel_one_fourth_x

            assert p1.coords[2][1] <= panel_three_fourths_y
            assert p1.coords[2][1] >= panel_one_fourth_y

        elif slice_skew == "tr":
            assert p1.coords[0][0] <= panel_three_fourths_x
            assert p1.coords[0][0] >= panel_one_fourth_x

            assert p1.coords[2][1] <= panel_three_fourths_y
            assert p1.coords[2][1] >= panel_one_fourth_y


@pytest.mark.parametrize(
    "horizontal_vertical, transform_type, pattern",
    [
        ("h", "trapezoid", "A"),
        ("h", "trapezoid", "V"),
        ("v", "trapezoid", "A"),
        ("v", "trapezoid", "V"),
        ("h", "rhombus", "left"),
        ("h", "rhombus", "right"),
        ("v", "rhombus", "left"),
        ("v", "rhombus", "right"),
    ]
)
def test_box_transform_panels(horizontal_vertical,
                              transform_type,
                              pattern,
                              make_panel
                              ):
    """
    This function tests whether the box_transform_panels function
    can:
    - Create a rhombus of 3 panels
    - Create a trapezoid of 3 panels
    - Do so for both horizontal and vertical panels


    :param horizontal_vertical:  Whether the panels should be horizontal
    or vertical

    :type horizontal_vertical: str

    :param transform_type: Whether the panels should be trapezoid
    or rhombuses

    :type transform_type: str

    :param pattern: Based on the type choice choose a pattern.
    For rhombus it's left or right, for trapezoid it's A or V
    defaults to None

    :type pattern: str

    :param make_panel: A function that outputs the desired panel type

    :type make_panel: function
    """

    # Since we've already tested draw_n above we can use it here.
    page = Page()

    draw_n(2, page, horizontal_vertical)
    next_div = invert_for_next(horizontal_vertical)
    panel = page.children[0]
    draw_n_shifted(3, page.children[0], next_div)
    page.num_panels = 3

    p1 = panel.get_child(0)
    p2 = panel.get_child(1)
    p3 = panel.get_child(2)

    # Original Coords
    op1 = deepcopy(p1.coords)
    op2 = deepcopy(p2.coords)
    op3 = deepcopy(p3.coords)

    # Transform panel
    box_transform_panels(page, type_choice=transform_type, pattern=pattern)

    p1 = panel.get_child(0)
    p2 = panel.get_child(1)
    p3 = panel.get_child(2)

    tp1 = p1.coords
    tp2 = p2.coords
    tp3 = p3.coords

    if transform_type == "trapezoid":
        if horizontal_vertical == "h":

            if pattern == "A":
                # Make sure that the transforms are moving the correct place

                # Line one
                # p1 x2y2  shifted right
                # p1 x3y3 shifted left
                assert op1[1][0] < tp1[1][0]
                assert op1[2][0] > tp1[2][0]

                # p2 x1y1 shifted right
                # p2 x4y4 shifted left
                assert op2[0][0] < tp2[0][0]
                assert op2[3][0] > tp2[3][0]

                # Box moved without gaps
                assert tp2[0][0] == tp1[1][0]
                assert tp2[3][0] == tp1[2][0]

                # Line two
                assert op2[1][0] > tp2[1][0]
                assert op2[2][0] < tp2[2][0]

                assert op3[0][0] > tp3[0][0]
                assert op3[3][0] < tp3[3][0]

                assert tp3[0][0] == tp2[1][0]
                assert tp3[3][0] == tp2[2][0]

            elif pattern == "V":

                # Line one
                assert op1[1][0] > tp1[1][0]
                assert op1[2][0] < tp1[2][0]

                assert op2[0][0] > tp2[0][0]
                assert op2[3][0] < tp2[3][0]

                # Box moved without gaps
                assert tp2[0][0] == tp1[1][0]
                assert tp2[3][0] == tp1[2][0]

                # Line two
                assert op2[1][0] < tp2[1][0]
                assert op2[2][0] > tp2[2][0]

                assert op3[0][0] < tp3[0][0]
                assert op3[3][0] > tp3[3][0]

                assert tp3[0][0] == tp2[1][0]
                assert tp3[3][0] == tp2[2][0]

        else:
            if pattern == "A":
                # Make sure that the transforms are moving the correct place

                # Line one
                assert op1[2][1] < tp1[2][1]
                assert op1[3][1] > tp1[3][1]

                assert op2[0][1] > tp2[0][1]
                assert op2[1][1] < tp2[1][1]

                # # Box moved without gaps
                assert tp2[1][1] == tp1[2][1]
                assert tp2[0][1] == tp1[3][1]

                # Line two
                assert op2[2][1] > tp2[2][1]
                assert op2[3][1] < tp2[3][1]

                assert op3[0][1] < tp3[0][1]
                assert op3[1][1] > tp3[1][1]

                assert tp3[0][1] == tp2[3][1]
                assert tp3[1][1] == tp2[2][1]

            elif pattern == "V":

                # Line one
                assert op1[2][1] > tp1[2][1]
                assert op1[3][1] < tp1[3][1]

                assert op2[0][1] < tp2[0][1]
                assert op2[1][1] > tp2[1][1]

                # # Box moved without gaps
                assert tp2[1][1] == tp1[2][1]
                assert tp2[0][1] == tp1[3][1]

                # Line two
                assert op2[2][1] < tp2[2][1]
                assert op2[3][1] > tp2[3][1]

                assert op3[0][1] > tp3[0][1]
                assert op3[1][1] < tp3[1][1]

                assert tp3[0][1] == tp2[3][1]
                assert tp3[1][1] == tp2[2][1]

    else:
        if horizontal_vertical == "h":
            if pattern == "left":

                # Line 1
                assert op1[1][0] > tp1[1][0]
                assert op1[2][0] < tp1[2][0]

                assert op2[0][0] > tp2[0][0]
                assert op2[3][0] < tp2[3][0]

                assert tp2[0][0] == tp1[1][0]
                assert tp2[3][0] == tp1[2][0]

                # Line 2
                assert op2[1][0] > tp2[1][0]
                assert op2[2][0] < tp2[2][0]

                assert op3[0][0] > tp3[0][0]
                assert op3[3][0] < tp3[3][0]

                assert tp2[1][0] == tp3[0][0]
                assert tp2[2][0] == tp3[3][0]

            else:
                # Line 1
                assert op1[1][0] < tp1[1][0]
                assert op1[2][0] > tp1[2][0]

                assert op2[0][0] < tp2[0][0]
                assert op2[3][0] > tp2[3][0]

                assert tp2[0][0] == tp1[1][0]
                assert tp2[3][0] == tp1[2][0]

                # Line 2
                assert op2[1][0] < tp2[1][0]
                assert op2[2][0] > tp2[2][0]

                assert op3[0][0] < tp3[0][0]
                assert op3[3][0] > tp3[3][0]

                assert tp2[1][0] == tp3[0][0]
                assert tp2[2][0] == tp3[3][0]

        else:
            if pattern == "left":

                # Line 1
                assert op1[2][1] > tp1[2][1]
                assert op1[3][1] < tp1[3][1]

                assert op2[0][1] < tp2[0][1]
                assert op2[1][1] > tp2[1][1]

                assert tp1[2][1] == tp2[1][1]
                assert tp1[3][1] == tp2[0][1]

                # Line 2
                assert op2[2][1] > tp2[2][1]
                assert op2[3][1] < tp2[3][1]

                assert op3[0][1] < tp3[0][1]
                assert op3[1][1] > tp3[1][1]

                assert tp2[2][1] == tp3[1][1]
                assert tp2[3][1] == tp3[0][1]
            else:

                # Line 1
                assert op1[2][1] < tp1[2][1]
                assert op1[3][1] > tp1[3][1]

                assert op2[0][1] > tp2[0][1]
                assert op2[1][1] < tp2[1][1]

                assert tp1[2][1] == tp2[1][1]
                assert tp1[3][1] == tp2[0][1]

                # Line 2
                assert op2[2][1] < tp2[2][1]
                assert op2[3][1] > tp2[3][1]

                assert op3[0][1] > tp3[0][1]
                assert op3[1][1] < tp3[1][1]

                assert tp2[2][1] == tp3[1][1]
                assert tp2[3][1] == tp3[0][1]


@pytest.mark.parametrize(
    "horizontal_vertical, num_panels, start_direction",
    [
        ("h", 2, "rup"),
        ("h", 3, "rup"),
        ("h", 4, "rup"),
        ("h", 5, "rup"),
        ("h", 6, "rup"),
        ("h", 7, "rup"),
        ("h", 8, "rup"),
        ("v", 2, "rup"),
        ("v", 3, "rup"),
        ("v", 4, "rup"),
        ("v", 5, "rup"),
        ("v", 6, "rup"),
        ("v", 7, "rup"),
        ("v", 8, "rup"),
        ("h", 2, "lup"),
        ("h", 3, "lup"),
        ("h", 4, "lup"),
        ("h", 5, "lup"),
        ("h", 6, "lup"),
        ("h", 7, "lup"),
        ("h", 8, "lup"),
        ("v", 2, "lup"),
        ("v", 3, "lup"),
        ("v", 4, "lup"),
        ("v", 5, "lup"),
        ("v", 6, "lup"),
        ("v", 7, "lup"),
        ("v", 8, "lup"),
    ]
)
def test_box_transform_page(horizontal_vertical, num_panels, start_direction):
    """
    This function tests if the function box_transform_page can:
    - Make a page's panels into rhombuses and trapezoids i.e. zigzag
    - Do so for 2 to 8 panels
    - Do so for vertical and horizontal panels
    - Do so for ONLY the edge case of having no children panels since
    the rest is tested in the move_children_to_line helper function

    :param horizontal_vertical: Whether the panels should be horizontal
    or vertical

    :type horizontal_vertical: str

    :param num_panels: Number of panels to put on page

    :type num_panels: int

    :param start_direction: Which direction should the first set of panels
    bend towards

    :type start_direction: str
    """

    # Since these functions are tested before it's alright to use them
    page = Page()
    draw_n_shifted(num_panels, page, horizontal_vertical)
    page.num_panels = num_panels
    direction_list = [start_direction]

    if len(page.children) > 2:
        for i in range(0, len(page.children) - 2):
            new_dir = np.random.choice(["rup", "lup"])
            direction_list.append(new_dir)

    # Transform page
    box_transform_page(page, direction_list=direction_list)

    for idx in range(0, len(page.children)-1):
        p1 = page.get_child(idx)
        p2 = page.get_child(idx+1)

        # If the first panel is horizontal therefore the second is too
        direction = direction_list[idx]
        if p1.orientation == "h":
            if direction == "rup":
                assert p1.x4y4[1] > p1.x3y3[1]
                assert p2.x1y1[1] > p2.x2y2[1]
            else:
                assert p1.x4y4[1] < p1.x3y3[1]
                assert p2.x1y1[1] < p2.x2y2[1]

            assert p1.x4y4[1] == p2.x1y1[1]
        else:
            if direction == "rup":
                assert p1.x2y2[0] < p1.x3y3[0]
                assert p2.x1y1[0] < p2.x4y4[0]
            else:
                assert p1.x2y2[0] > p1.x3y3[0]
                assert p2.x1y1[0] > p2.x4y4[0]

            assert p1.x2y2[0] == p2.x1y1[0]


def assess_hiearchy(parent, hiearchy):
    """
    This function is a helper function used
    to return the hiearchy of the panels within a
    page to asess whether they were created properly
    as well as in the right orientation

    :param parent: The parent panel to get children from

    :type parent: Panel

    :param hiearchy: A dictionary containing the
    hiearchy

    :type hiearchy: dict
    """

    if len(parent.children) > 0:
        hiearchy[parent.name] = {}
        for child in parent.children:

            # Check orientation'
            if parent.orientation == "h":
                assert child.orientation == "v"
            elif parent.orientation == "v":
                assert child.orientation == "h"
            # Case for parent is page
            else:
                pass

            assess_hiearchy(child, hiearchy)
    else:
        if parent.parent is None:
            pass
        else:
            hiearchy[parent.parent.name][parent.name] = None


@pytest.mark.parametrize(
    "num_panels, layout_type, layout_choice",
    [
        (1, None, None),
        (2, "v", None),
        (2, "h", None),
        (2, "vh", None),
        (3, "h", None),
        (3, "v", None),
        (3, "vh", None),
        (4, "v", None),
        (4, "h", None),
        (4, "vh", "eq"),
        (4, "vh", "uneq"),
        (4, "vh", "div"),
        (4, "vh", "trip"),
        (4, "vh", "twoonethree"),
        (5, "h", None),
        (5, "vh", "eq"),
        (5, "vh", "uneq"),
        (5, "vh", "div"),
        (5, "vh", "twotwothree"),
        (5, "vh", "threetwotwo"),
        (5, "vh", "fourtwoone"),
        (6, "vh", "tripeq"),
        (6, "vh", "tripuneq"),
        (6, "vh", "twofourtwo"),
        (6, "vh", "twothreethree"),
        (6, "vh", "fourtwotwo"),
        (7, "vh", "twothreefour"),
        (7, "vh", "threethreetwotwo"),
        (7, "vh", "threefourtwoone",),
        (7, "vh", "threethreextwoone"),
        (7, "vh", "fourthreextwo"),
        (8, "vh", "fourfourxtwoeq"),
        (8, "vh", "fourfourxtwouneq"),
        (8, "vh", "threethreethreetwo"),
        (8, "vh", "threefourtwotwo"),
        (8, "vh", "threethreefourone"),
    ]
)
def test_get_base_panels(num_panels, layout_type, layout_choice):
    """
    This function evalutes the get_base_panels function for:
    - Producing the correct hiearchy of panels - TODO
    - Testing them for the correct orientation
    - Testing the edge case of 1 panel that is just
    a page being blank

    :param num_panels: how many panels should be on a page

    :type num_panels: int

    :param layout_type: whether the page should consist of
    vertical, horizontal or both types of panels

    :type layout_type: str

    :param layout_choice: If having selected vh panels select a type
    of layout specifically

    :type layout_choice: str
    """

    page = get_base_panels(num_panels, layout_type, layout_choice, "test")
    leaf_children = []
    get_leaf_panels(page, leaf_children)

    if num_panels > 1:
        assert len(leaf_children) == num_panels

    # Currently only sees if the orientations are correct
    hiearchy = {}
    assess_hiearchy(page, hiearchy)
