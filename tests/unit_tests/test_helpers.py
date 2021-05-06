import pytest
import math
from preprocesing.layout_engine.helpers import (
                        get_min_area_panels,
                        move_child_to_line,
                        move_children_to_line,
                        invert_for_next
)

from preprocesing.layout_engine.page_dataset_creator import (
    get_base_panels,
    get_leaf_panels,
    move_children_to_line

)
from preprocesing.layout_engine.page_dataset_creator import (
    draw_n
)

from preprocesing.layout_engine.page_object_classes import Page

@pytest.mark.parametrize(
    "min_area",
    [
        0.1,
        0.2,
        0.3,
        0.4,
        0.5,
    ]
)
def test_get_min_area_panel(min_area):
    """
    This function tests whether the get_min_area_panels function
    actually returns leaf panels with the correct area proprtion

    :param min_area: Minimum area requirement

    :type min_area: float
    """

    page = get_base_panels()

    leaf_children = []
    get_leaf_panels(page, leaf_children)

    correct_panels = []
    for child in leaf_children:
        if child.area_proportion >= min_area:
            correct_panels.append(child.name)

    test_panels = []
    get_min_area_panels(page, min_area, test_panels)

    test_panels = [p.name for p in test_panels]
    assert test_panels == correct_panels


def distance(a, b):
    """
    Helper function for checking distance
    between any two points on a cartesian grid

    :param a: First point

    :type a: tuple

    :param b: Second point

    :type b: tuple

    :return: Distance between two points

    :rtype: float
    """

    return math.sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2)

@pytest.mark.parametrize(
    "horizontal_vertical, line_direction, change",
    [
        ("h", "lup", 0.1),
        ("h", "rup", 0.1),
        ("v", "lup", 0.1),
        ("v", "rup", 0.1),
        ("h", "lup", 0.2),
        ("h", "rup", 0.2),
        ("v", "lup", 0.2),
        ("v", "rup", 0.2),
        ("h", "lup", 0.3),
        ("h", "rup", 0.3),
        ("v", "lup", 0.3),
        ("v", "rup", 0.3),
        ("h", "lup", 0.4),
        ("h", "rup", 0.4),
        ("v", "lup", 0.4),
        ("v", "rup", 0.4),
        ("h", "lup", 0.5),
        ("h", "rup", 0.5),
        ("v", "lup", 0.5),
        ("v", "rup", 0.5),

    ]
)
def test_move_children_to_line(horizontal_vertical, line_direction, change):
    """
    This function tests if the move children to line
    function actually moves the correct children of a shifted
    panel to a line. The scenarios tested are:
    - Horizontal Panels, Vertical Panels
    - Line going Right Up/Left Up
    """

    page = Page()
    page.num_panels = 6

    # Split page onece
    draw_n(2, page, horizontal_vertical)
    p1 = page.get_child(0)
    p2 = page.get_child(1)

    # Pick one panel of the split page and split it again
    next_div = invert_for_next(horizontal_vertical)
    draw_n(2, p2, next_div)
    p3 = p2.get_child(0)

    # Pick one of these and split it into 4
    next_div = invert_for_next(horizontal_vertical)
    draw_n(4, p3, next_div)

    # Get the maximum possible shift distance
    change_max = min([(p1.x4y4[1] - p1.x1y1[1]),
                     (p2.x4y4[1] - p2.x1y1[1])])

    # get change in real number terms
    line_change = change_max*change

    # Define old line
    if horizontal_vertical == "h":
        line_top = p2.x1y1
        line_bottom = p2.x2y2
    else:
        line_top = p2.x1y1
        line_bottom = p2.x4y4

    # Move the children of the page
    move_children_to_line(p2,
                          (
                              line_top,
                              line_bottom,
                          ),
                          line_change,
                          horizontal_vertical,
                          line_direction
                          )

    points_to_evaluate = []
    new_line = []

    if horizontal_vertical == "h":

        # Points which we know should move
        p4 = p2.get_child(1)
        points_to_evaluate.append(p4.x1y1)
        points_to_evaluate.append(p4.x2y2)

        for child in p3.children:
            points_to_evaluate.append(child.x1y1)
            points_to_evaluate.append(child.x2y2)

        # Construct the new line
        if line_direction == "lup":

            new_line = [
                (p2.x1y1[0], p2.x1y1[1] - line_change),
                p2.x2y2
            ]
        else:
            new_line = [
                (p2.x1y1[0], p2.x1y1[1] + line_change),
                p2.x2y2
            ]
    else:

        p4 = p2.get_child(1)
        points_to_evaluate.append(p4.x1y1)
        points_to_evaluate.append(p4.x4y4)

        for child in p3.children:
            points_to_evaluate.append(child.x1y1)
            points_to_evaluate.append(child.x4y4)

        if line_direction == "lup":

            new_line = [
                (p2.x1y1[0] - line_change, p2.x1y1[1]),
                p2.x4y4
            ]
        else:
            new_line = [
                (p2.x1y1[0] + line_change, p2.x1y1[1]),
                p2.x4y4
            ]

    # Use the idea that distance(A, B)
    # equals distance(A, C) + distance(B, C)
    # If C is on the line
    total_dist = distance(new_line[0], new_line[1])

    for point in points_to_evaluate:

        a_c = distance(new_line[0], point)
        b_c = distance(new_line[1], point)

        diff = total_dist - (a_c + b_c)

        # float comparison
        assert diff < 1e-12
