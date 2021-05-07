import numpy as np
import math
import time
from copy import deepcopy
import random
from PIL import Image, ImageDraw, ImageFont
import pyclipper
import json
import uuid

from .page_object_classes import Panel, Page, SpeechBubble
from .helpers import (
                      invert_for_next, choose, choose_and_return_other,
                      get_min_area_panels, get_leaf_panels,
                      find_parent_with_multiple_children,
                      move_children_to_line
                      )
from .. import config_file as cfg


# Creation helpers
def draw_n_shifted(n, parent, horizontal_vertical, shifts=[]):
    """
    A function to take a parent Panel and divide it into n
    sub-panel's vertically or horizontally with each panels having
    specified size ratios along the axis perpendicular to their orientation

    NOTE: This function performs actions by reference

    :param n: Number of sub-panels

    :type n: int

    :param parent: The parent panel being split

    :type parent: Panel

    :param horizontal_vertical: Whether to render the sub-panels vertically
    or horizontally in regards to the page

    :type horizontal_vertical: str

    :param shifts: Ratios to divide the panel into sub-panels

    :type shifts: list
    """

    # if input out of bounds i.e. 1:
    if n == 1:
        return parent

    # Specify parent panel dimensions
    topleft = parent.x1y1
    topright = parent.x2y2
    bottomright = parent.x3y3
    bottomleft = parent.x4y4

    # Allow each inital panel to grow to up to 150% of 100/n
    # which would be all panel's equal.
    # This is then normalized down to a smaller number
    choice_max = round((100/n)*1.5)
    choice_min = round((100/n)*0.5)

    normalized_shifts = []

    # If there are no ratios specified
    if len(shifts) < 1:
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
    else:
        normalized_shifts = shifts

    # If the panel is horizontal to the page
    if horizontal_vertical == "h":
        shift_level = 0.0

        # For each new panel
        for i in range(0, n):
            # If it's the first panel then it's
            # has the same left side as the parent top side
            if i == 0:
                x1y1 = topleft
                x2y2 = topright

            # If not it has the same top side as it's previous
            # sibiling's bottom side
            else:
                # this shift level is the same as the bottom side
                # of the sibling panel
                shift_level += normalized_shifts[i-1]

                # Specify points for the top side
                x1y1 = (bottomleft[0],
                        topleft[1] +
                        (bottomleft[1] - topleft[1])*shift_level)

                x2y2 = (bottomright[0],
                        topright[1] +
                        (bottomright[1] - topright[1])*shift_level)

            # If it's the last panel then it has the
            # same right side as the parent bottom side
            if i == (n-1):
                x3y3 = bottomright
                x4y4 = bottomleft

            # If not it has the same bottom side as it's next
            # sibling's top side
            else:
                # Same shift level as the left side of next sibling
                next_shift_level = shift_level + normalized_shifts[i]

                # Specify points for the bottom side
                x3y3 = (bottomright[0], topright[1] +
                        (bottomright[1] - topright[1])*next_shift_level)

                x4y4 = (bottomleft[0], topleft[1] +
                        (bottomleft[1] - topleft[1])*next_shift_level)

            # Create a Panel
            poly_coords = (x1y1, x2y2, x3y3, x4y4, x1y1)
            poly = Panel(poly_coords,
                         parent.name+"-"+str(i),
                         orientation=horizontal_vertical,
                         parent=parent,
                         children=[]
                         )

            parent.add_child(poly)

    # If the panel is vertical
    if horizontal_vertical == "v":
        shift_level = 0.0

        # For each new panel
        for i in range(0, n):

            # If it's the first panel it has the same
            # top side as the parent's left side
            if i == 0:
                x1y1 = topleft
                x4y4 = bottomleft

            # if not it's left side is the same as it's
            # previous sibling's right side
            else:
                # Same shift level as the right side of previous sibling
                shift_level += normalized_shifts[i-1]

                # Specify points for left side
                x1y1 = (topleft[0] +
                        (topright[0] - topleft[0])*shift_level,
                        topright[1])

                x4y4 = (bottomleft[0] +
                        (bottomright[0] - bottomleft[0])*shift_level,
                        bottomright[1])

            # If it's the last panel i thas the same
            # right side as it's parent panel
            if i == (n-1):
                x2y2 = topright
                x3y3 = bottomright

            # If not then it has the same right side as it's next sibling's
            # left side
            else:
                # Same shift level as next sibling's left side
                next_shift_level = shift_level + normalized_shifts[i]

                # Specify points for right side
                x2y2 = (topleft[0] +
                        (topright[0] - topleft[0])*next_shift_level,
                        topright[1])

                x3y3 = (bottomleft[0] +
                        (bottomright[0] - bottomleft[0])*next_shift_level,
                        bottomright[1])

            # Create a panel
            poly_coords = (x1y1, x2y2, x3y3, x4y4, x1y1)
            poly = Panel(poly_coords,
                         parent.name+"-"+str(i),
                         orientation=horizontal_vertical,
                         parent=parent,
                         children=[]
                         )

            parent.add_child(poly)


def draw_n(n, parent, horizontal_vertical):
    """
    A function to take a parent Panel and divide it into n
    sub-panel's vertically or horizontally with each panels having
    equal size ratios along the axis perpendicular to their orientation


    NOTE: This function performs actions by reference

    :param n: Number of sub-panels

    :type n: int

    :param parent: The parent panel being split

    :type parent: Panel

    :param horizontal_vertical: Whether to render the sub-panels vertically
    or horizontally in regards to the page

    :type horizontal_vertical: str
    """
    # if input out of bounds i.e. 1:
    if n == 1:
        return parent

    # Specify parent panel dimensions
    topleft = parent.x1y1
    topright = parent.x2y2
    bottomright = parent.x3y3
    bottomleft = parent.x4y4

    # If the panel is horizontal to the page
    if horizontal_vertical == "h":

        # For each new panel
        for i in range(0, n):

            # If it's the first panel then it's
            # has the same left side as the parent top side
            if i == 0:
                x1y1 = topleft
                x2y2 = topright
            # If not it has the same top side as it's
            # previous sibiling's bottom side
            else:

                # Specify points for the top side
                # Since it's equally divided the size is dictated by (i/n)
                x1y1 = (bottomleft[0],
                        topleft[1] + (bottomleft[1] - topleft[1])*(i/n))

                x2y2 = (bottomright[0],
                        topright[1] + (bottomright[1] - topright[1])*(i/n))

            # If it's the last panel then it has the
            # same right side as the parent bottom side
            if i == (n-1):
                x3y3 = bottomright
                x4y4 = bottomleft

            # If not it has the same bottom side as it's
            # next sibling's top side
            else:
                # Specify points for the bottom side
                # Since it's equally divided the size is dictated by (i/n)
                x3y3 = (bottomright[0],
                        topright[1] + (bottomright[1] - topright[1])*((i+1)/n))
                x4y4 = (bottomleft[0],
                        topleft[1] + (bottomleft[1] - topleft[1])*((i+1)/n))

            # Create a Panel
            poly_coords = (x1y1, x2y2, x3y3, x4y4, x1y1)
            poly = Panel(poly_coords,
                         parent.name+"-"+str(i),
                         orientation=horizontal_vertical,
                         parent=parent,
                         children=[]
                         )

            parent.add_child(poly)

    # If the panel is vertical
    if horizontal_vertical == "v":
        # For each new panel
        for i in range(0, n):

            # If it's the first panel it has the same
            # top side as the parent's left side
            if i == 0:
                x1y1 = topleft
                x4y4 = bottomleft

            # If not it's left side is the same as it's
            # previous sibling's right side
            else:
                # Specify points for left side
                # Since it's equally divided the size is dictated by (i/n)
                x1y1 = (topleft[0] +
                        (topright[0] - topleft[0])*(i/n),
                        topright[1])

                x4y4 = (bottomleft[0] +
                        (bottomright[0] - bottomleft[0])*(i/n),
                        bottomright[1])

            # If it's the last panel i thas the same
            # right side as it's parent panel
            if i == (n-1):
                x2y2 = topright
                x3y3 = bottomright

            # If not then it has the same right side as it's next sibling's
            # left side
            else:
                # Specify points for right side
                # Since it's equally divided the size is dictated by (i/n)
                x2y2 = (topleft[0] +
                        (topright[0] - topleft[0])*((i+1)/n),
                        topright[1])

                x3y3 = (bottomleft[0] +
                        (bottomright[0] - bottomleft[0])*((i+1)/n),
                        bottomright[1])

            poly_coords = (x1y1, x2y2, x3y3, x4y4, x1y1)
            poly = Panel(poly_coords,
                         parent.name+"-"+str(i),
                         orientation=horizontal_vertical,
                         parent=parent,
                         children=[]
                         )

            parent.add_child(poly)


def draw_two_shifted(parent, horizontal_vertical, shift=None):
    """
    Draw two subpanels of a parent panel

    :param parent: The parent panel to be split

    :type parent: Parent

    :param horizontal_vertical: Orientation of sub-panels in refrence
    to the page

    :type horizontal_vertical: str

    :param shift: by what ratio should the 2 panels be split, defaults to None

    :type shift: float, optional
    """

    # Specify parent panel dimensions
    topleft = parent.x1y1
    topright = parent.x2y2
    bottomright = parent.x3y3
    bottomleft = parent.x4y4

    # If shift's are not specified select them
    if shift is None:
        shift_min = 25
        shift_max = 75
        shift = np.random.randint(shift_min, shift_max)
        shift = shift/100

    # If panel is horizontal
    if horizontal_vertical == "h":

        # Spcify the first panel's coords
        r1x1y1 = topleft
        r1x2y2 = topright
        r1x3y3 = (bottomright[0],
                  topright[1] + (bottomright[1] - topright[1])*shift)
        r1x4y4 = (bottomleft[0],
                  topleft[1] + (bottomleft[1] - topleft[1])*shift)

        poly1_coords = (r1x1y1, r1x2y2, r1x3y3, r1x4y4, r1x1y1)

        # Specify the second panel's coords
        r2x1y1 = (bottomleft[0],
                  topleft[1] + (bottomleft[1] - topleft[1])*shift)
        r2x2y2 = (bottomright[0],
                  topright[1] + (bottomright[1] - topright[1])*shift)

        r2x3y3 = bottomright
        r2x4y4 = bottomleft

        poly2_coords = (r2x1y1, r2x2y2, r2x3y3, r2x4y4, r2x1y1)

        # Create panels
        poly1 = Panel(poly1_coords,
                      parent.name + "-0",
                      orientation=horizontal_vertical,
                      parent=parent,
                      children=[])

        poly2 = Panel(poly2_coords,
                      parent.name + "-1",
                      orientation=horizontal_vertical,
                      parent=parent,
                      children=[])

        parent.add_children([poly1, poly2])

    # If the panel is vertical
    if horizontal_vertical == "v":

        # Specify the first panel's coords
        r1x1y1 = topleft
        r1x2y2 = (topleft[0] + (topright[0] - topleft[0])*shift, topright[1])
        r1x3y3 = (bottomleft[0] + (bottomright[0] - bottomleft[0])*shift,
                  bottomright[1])
        r1x4y4 = bottomleft

        poly1_coords = (r1x1y1, r1x2y2, r1x3y3, r1x4y4, r1x1y1)

        # Specify the second panel's coords
        r2x1y1 = (topleft[0] + (topright[0] - topleft[0])*shift, topright[1])
        r2x2y2 = topright
        r2x3y3 = bottomright
        r2x4y4 = (bottomleft[0] + (bottomright[0] - bottomleft[0])*shift,
                  bottomright[1])

        poly2_coords = (r2x1y1, r2x2y2, r2x3y3, r2x4y4, r2x1y1)

        # Create panels
        poly1 = Panel(poly1_coords,
                      parent.name + "-0",
                      orientation=horizontal_vertical,
                      parent=parent,
                      children=[])

        poly2 = Panel(poly2_coords,
                      parent.name + "-1",
                      orientation=horizontal_vertical,
                      parent=parent,
                      children=[])

        parent.add_children([poly1, poly2])


# Page transformations
def single_slice_panels(page,
                        horizontal_vertical=None,
                        type_choice=None,
                        skew_side=None,
                        number_to_slice=0
                        ):
    """Slices a panel once at an angle into two new panels

    :param page: Page to have panels sliced

    :type page: Page

    :param horizontal_vertical:  Whether the slice should be horizontal
    or vertical

    :type horizontal_vertical: str

    :param type_choice: Specify whether the panel should be
    sliced down the "center" or on a "side", defaults to None

    :type type_choice: str, optional

    :param skew_side: Based on the type of slicing which direction should
    it be sliced

    :type skew_side: str

    :param number_to_slice: Number of panels to slice

    :type number_to_slice: int

    :return: page with sliced panels

    :rtype: Page
    """

    # Remove panels which are too small
    relevant_panels = []
    if len(page.children) > 0:
        get_min_area_panels(page,
                            cfg.slice_minimum_panel_area,
                            ret_panels=relevant_panels
                            )
    else:
        relevant_panels = [page]

    # Shuffle panels for randomness
    random.shuffle(relevant_panels)

    # single slice close
    if type_choice is None:
        type_choice_prob = np.random.random()
        if type_choice_prob < cfg.center_side_ratio:
            type_choice = "center"
        else:
            type_choice = "side"

    num_panels_added = 0

    # Slice panels down the center
    if type_choice == "center":
        if len(relevant_panels) < 1:
            return page

        if number_to_slice == 0:
            if len(relevant_panels) > 1:
                number_to_slice = np.random.randint(1, len(relevant_panels))
            else:
                number_to_slice = 1

        for idx in range(0, number_to_slice):
            panel = relevant_panels[idx]
            num_panels_added += 1

            # Decide which direction to cut in
            if horizontal_vertical is None:
                horizontal_vertical = np.random.choice(["h", "v"])

            # Get center line
            # Vertical slice
            if horizontal_vertical == "v":
                panel_chosen_coord_length = (panel.x2y2[0] - panel.x1y1[0])/2

                # Slice panel
                draw_n(2, panel, "v")

                # Skew it left or right
                if skew_side is None:
                    skew_side = np.random.choice(["left", "right"])

                # Skew it by a percentage
                skew_amount = np.random.randint(20, 100)/100
                skew_amount = skew_amount*panel_chosen_coord_length

                # Perform transform
                p1 = panel.get_child(0)
                p2 = panel.get_child(1)

                p1.sliced = True
                p2.sliced = True
                if skew_side == "left":
                    p1.x2y2 = (p1.x2y2[0] - skew_amount, p1.x2y2[1])
                    p1.x3y3 = (p1.x3y3[0] + skew_amount, p1.x3y3[1])

                    p1.refresh_coords()

                    p2.x1y1 = (p2.x1y1[0] - skew_amount, p2.x1y1[1])
                    p2.x4y4 = (p2.x4y4[0] + skew_amount, p2.x4y4[1])

                    p2.refresh_coords()

                elif skew_side == "right":
                    p1.x2y2 = (p1.x2y2[0] + skew_amount, p1.x2y2[1])
                    p1.x3y3 = (p1.x3y3[0] - skew_amount, p1.x3y3[1])

                    p1.refresh_coords()

                    p2.x1y1 = (p2.x1y1[0] + skew_amount, p2.x1y1[1])
                    p2.x4y4 = (p2.x4y4[0] - skew_amount, p2.x4y4[1])

                    p2.refresh_coords()

                else:
                    print("Chosen incorrect skew side")
                    return None

            # Horizontal slice
            else:
                panel_chosen_coord_length = (panel.x3y3[1] - panel.x2y2[1])/2

                # Slice panel
                draw_n(2, panel, "h")

                # Skew it left or right
                if skew_side is None:
                    skew_side = np.random.choice(["down", "up"])

                # Skew it by a percentage
                skew_amount = np.random.randint(20, 100)/100
                skew_amount = skew_amount*panel_chosen_coord_length

                p1 = panel.get_child(0)
                p2 = panel.get_child(1)

                p1.sliced = True
                p2.sliced = True
                if skew_side == "down":
                    p1.x4y4 = (p1.x4y4[0], p1.x4y4[1] + skew_amount)
                    p1.x3y3 = (p1.x3y3[0], p1.x3y3[1] - skew_amount)

                    p1.refresh_coords()

                    p2.x1y1 = (p2.x1y1[0], p2.x1y1[1] + skew_amount)
                    p2.x2y2 = (p2.x2y2[0], p2.x2y2[1] - skew_amount)

                    p2.refresh_coords()

                elif skew_side == "up":
                    p1.x4y4 = (p1.x4y4[0], p1.x4y4[1] - skew_amount)
                    p1.x3y3 = (p1.x3y3[0], p1.x3y3[1] + skew_amount)

                    p1.refresh_coords()

                    p2.x1y1 = (p2.x1y1[0], p2.x1y1[1] - skew_amount)
                    p2.x2y2 = (p2.x2y2[0], p2.x2y2[1] + skew_amount)

                    p2.refresh_coords()
                else:
                    print("Chose incorrect skew_side")

    # Slice panel sides
    else:
        if len(relevant_panels) < 1:
            return page

        if number_to_slice == 0:
            if len(relevant_panels) > 1:
                number_to_slice = np.random.choice([1, 3])
            else:
                number_to_slice = 1

        for panel in relevant_panels[0:number_to_slice]:

            if skew_side is None:
                skew_side = np.random.choice(["tr", "tl", "br", "bl"])

            draw_n(2, panel, "h")
            num_panels_added += 1

            p1 = panel.get_child(0)
            p2 = panel.get_child(1)

            # Panels are non standard polygons
            p1.non_rect = True
            p2.non_rect = True

            p1.sliced = True
            p2.sliced = True

            cut_y_proportion = np.random.randint(25, 75)/100
            cut_x_proportion = np.random.randint(25, 75)/100

            cut_y_length = (panel.x4y4[1] - panel.x1y1[1])*cut_y_proportion
            cut_x_length = (panel.x3y3[0] - panel.x4y4[0])*cut_x_proportion

            # bottom left corner
            if skew_side == "bl":

                p1_cut_x1y1 = (panel.x4y4[0], panel.x4y4[1] - cut_y_length)
                p1_cut_x2y2 = (panel.x4y4[0] + cut_x_length, panel.x4y4[1])
                p1_cut_x3y3 = (panel.x4y4)

                p1.coords = [p1_cut_x1y1, p1_cut_x2y2,
                             p1_cut_x3y3, p1_cut_x1y1]

                p2.coords = [panel.x1y1, panel.x2y2, panel.x3y3,
                             p1_cut_x2y2, p1_cut_x1y1, panel.x1y1]

            # bottom right corner
            elif skew_side == "br":

                p1_cut_x1y1 = (panel.x3y3[0], panel.x3y3[1] - cut_y_length)
                p1_cut_x2y2 = (panel.x3y3)
                p1_cut_x3y3 = (panel.x3y3[0] - cut_x_length, panel.x3y3[1])

                p1.coords = [p1_cut_x1y1, p1_cut_x2y2,
                             p1_cut_x3y3, p1_cut_x1y1]

                p2.coords = [panel.x1y1, panel.x2y2, p1_cut_x1y1,
                             p1_cut_x3y3, panel.x4y4, panel.x1y1]

            # top left corner
            elif skew_side == "tl":

                p1_cut_x1y1 = panel.x1y1
                p1_cut_x2y2 = (panel.x1y1[0] + cut_x_length, panel.x1y1[1])
                p1_cut_x3y3 = (panel.x1y1[0], panel.x1y1[1] + cut_y_length)

                p1.coords = [p1_cut_x1y1, p1_cut_x2y2,
                             p1_cut_x3y3, p1_cut_x1y1]
                p2.coords = [p1_cut_x2y2, panel.x2y2, panel.x3y3,
                             panel.x4y4, p1_cut_x3y3, p1_cut_x1y1]

            # top right corner
            elif skew_side == "tr":
                p1_cut_x1y1 = (panel.x2y2[0] - cut_x_length, panel.x2y2[1])
                p1_cut_x2y2 = panel.x2y2
                p1_cut_x3y3 = (panel.x2y2[0], panel.x2y2[1] + cut_y_length)

                p1.coords = [p1_cut_x1y1, p1_cut_x2y2,
                             p1_cut_x3y3, p1_cut_x1y1]

                p2.coords = [panel.x1y1, p1_cut_x1y1, p1_cut_x3y3,
                             panel.x3y3, panel.x4y4, panel.x1y1]
            else:
                print("Chose incorrect skew side")
                return None

    page.num_panels += num_panels_added

    return page


def box_transform_panels(page, type_choice=None, pattern=None):
    """
    This function move panel boundaries to transform them
    into trapezoids and rhombuses

    :param page: Page to be transformed

    :type page: Page

    :param type_choice: If you want to specify
    a particular transform type: rhombus or trapezoid, defaults to None

    :type type_choice: str, optional

    :param pattern: Based on the type choice choose a pattern.
    For rhombus it's left or right, for trapezoid it's A or V
    defaults to None

    :type pattern: str, optional

    :return: Transformed Page

    :rtype: Page
    """

    if type_choice is None:
        type_choice_prob = np.random.random()
        if type_choice_prob < cfg.panel_box_trapezoid_ratio:
            type_choice = "trapezoid"
        else:
            type_choice = "rhombus"

    if type_choice == "trapezoid":
        if page.num_panels > 2:

            # Get parent panel which satisfies the criteria for the transform
            relevant_panels = find_parent_with_multiple_children(page, 3)

            if len(relevant_panels) > 0:
                if len(relevant_panels) > 1:
                    num_panels = np.random.randint(1, len(relevant_panels))
                else:
                    num_panels = 1

                # For each panel
                for idx in range(0, num_panels):
                    panel = relevant_panels[idx]

                    # Get the three child panels
                    # Since panels are created in order
                    p1 = panel.get_child(0)
                    p2 = panel.get_child(1)
                    p3 = panel.get_child(2)

                    min_width = math.inf
                    min_height = math.inf

                    # Get the smallest height and width
                    for child in [p1, p2, p3]:

                        if child.width < min_width:
                            min_width = child.width

                        if child.height < min_height:
                            min_height = child.height

                    # Choose trapezoid pattern
                    if pattern is None:
                        trapezoid_pattern = np.random.choice(["A", "V"])
                    else:
                        trapezoid_pattern = pattern

                    movement_proportion = np.random.randint(
                                            10,
                                            cfg.trapezoid_movement_limit)

                    # If parent panel is horizontal the children are vertical
                    if panel.orientation == "h":

                        # Get how much the lines of the child panels move
                        # on the x axis to make the trapezoid
                        x_movement = min_width*(movement_proportion/100)

                        # Make an A pattern horizontally
                        if trapezoid_pattern == "A":

                            # Get the coords of the first line to be moved
                            line_one_top = (p1.x2y2[0] + x_movement,
                                            p1.x2y2[1])

                            line_one_bottom = (p1.x3y3[0] - x_movement,
                                               p1.x3y3[1])

                            # Move line between child 1 and 2
                            p1.x2y2 = line_one_top
                            p1.x3y3 = line_one_bottom

                            p1.refresh_coords()

                            p2.x1y1 = line_one_top
                            p2.x4y4 = line_one_bottom

                            # Get the coords of the second line to be moved
                            line_two_top = (p2.x2y2[0] - x_movement,
                                            p2.x2y2[1])
                            line_two_bottom = (p2.x3y3[0] + x_movement,
                                               p2.x3y3[1])

                            # Move line two between child 2 and 3
                            p2.x2y2 = line_two_top
                            p2.x3y3 = line_two_bottom

                            p2.refresh_coords()

                            p3.x1y1 = line_two_top
                            p3.x4y4 = line_two_bottom

                            p3.refresh_coords()

                        # Make a V pattern horizontally
                        else:

                            # Get the coords of the first line to be moved
                            line_one_top = (p1.x2y2[0] - x_movement,
                                            p1.x2y2[1])

                            line_one_bottom = (p1.x3y3[0] + x_movement,
                                               p1.x3y3[1])

                            # Move line between child 1 and 2
                            p1.x2y2 = line_one_top
                            p1.x3y3 = line_one_bottom

                            p1.refresh_coords()

                            p2.x1y1 = line_one_top
                            p2.x4y4 = line_one_bottom

                            # Get the coords of the second line to be moved
                            line_two_top = (p2.x2y2[0] + x_movement,
                                            p2.x2y2[1])

                            line_two_bottom = (p2.x3y3[0] - x_movement,
                                               p2.x3y3[1])

                            # Move line two between child 2 and 3
                            p2.x2y2 = line_two_top
                            p2.x3y3 = line_two_bottom

                            p2.refresh_coords()

                            p3.x1y1 = line_two_top
                            p3.x4y4 = line_two_bottom

                            p3.refresh_coords()

                    # If panel is vertical children are horizontal
                    # so the A and the V are at 90 degrees to the page
                    else:
                        # Get how much the lines of the child panels move
                        # on the y axis to make the trapezoid
                        y_movement = min_height*(movement_proportion/100)

                        # Make an A pattern vertically
                        if trapezoid_pattern == "A":

                            # Get the coords of the first line to be moved
                            line_one_top = (p2.x2y2[0],
                                            p2.x2y2[1] + y_movement)

                            line_one_bottom = (p2.x1y1[0],
                                               p2.x1y1[1] - y_movement)

                            # Move line between child 1 and 2
                            p2.x2y2 = line_one_top
                            p2.x1y1 = line_one_bottom

                            p1.x3y3 = line_one_top
                            p1.x4y4 = line_one_bottom

                            p1.refresh_coords()

                            # Get the coords of the second line to be moved
                            line_two_top = (p2.x3y3[0],
                                            p2.x3y3[1] - y_movement)

                            line_two_bottom = (p2.x4y4[0],
                                               p2.x4y4[1] + y_movement)

                            # Move line two between child 2 and 3
                            p2.x3y3 = line_two_top
                            p2.x4y4 = line_two_bottom

                            p2.refresh_coords()

                            p3.x1y1 = line_two_bottom
                            p3.x2y2 = line_two_top

                            p3.refresh_coords()
                        # Make a V pattern vertically
                        else:

                            # Get the coords of the first line to be moved
                            line_one_top = (p2.x2y2[0],
                                            p2.x2y2[1] - y_movement)

                            line_one_bottom = (p2.x1y1[0],
                                               p2.x1y1[1] + y_movement)

                            # Move line between child 1 and 2
                            p2.x2y2 = line_one_top
                            p2.x1y1 = line_one_bottom

                            p1.x3y3 = line_one_top
                            p1.x4y4 = line_one_bottom

                            p1.refresh_coords()
                            # Get the coords of the second line to be moved
                            line_two_top = (p2.x3y3[0],
                                            p2.x3y3[1] + y_movement)

                            line_two_bottom = (p2.x4y4[0],
                                               p2.x4y4[1] - y_movement)

                            # Move line two between child 2 and 3
                            p2.x3y3 = line_two_top
                            p2.x4y4 = line_two_bottom

                            p2.refresh_coords()
                            p3.x1y1 = line_two_bottom
                            p3.x2y2 = line_two_top

                            p3.refresh_coords()

    elif type_choice == "rhombus":

        if page.num_panels > 1:

            # Get parent panel which satisfies the criteria for the transform
            relevant_panels = find_parent_with_multiple_children(page, 3)

            if len(relevant_panels) > 0:

                if len(relevant_panels) > 1:
                    num_panels = np.random.randint(1, len(relevant_panels))
                else:
                    num_panels = 1

                for idx in range(0, num_panels):

                    panel = relevant_panels[idx]

                    # Since panels are created in order
                    p1 = panel.get_child(0)
                    p2 = panel.get_child(1)
                    p3 = panel.get_child(2)

                    min_width = math.inf
                    min_height = math.inf

                    # Get the smallest height and width
                    for child in [p1, p2, p3]:

                        if child.width < min_width:
                            min_width = child.width

                        if child.height < min_height:
                            min_height = child.height

                    if pattern is None:
                        rhombus_pattern = np.random.choice(["left", "right"])
                    else:
                        rhombus_pattern = pattern

                    movement_proportion = np.random.randint(
                                            10,
                                            cfg.rhombus_movement_limit
                                            )

                    # Logic for the section below is the same as the
                    # trapezoid with the exception of the fact that the
                    # rhombus pattern happens to move both lines in the
                    # same direction

                    if panel.orientation == "h":

                        x_movement = min_width*(movement_proportion/100)

                        if rhombus_pattern == "left":
                            line_one_top = (p1.x2y2[0] - x_movement,
                                            p1.x2y2[1])

                            line_one_bottom = (p1.x3y3[0] + x_movement,
                                               p1.x3y3[1])

                            p1.x2y2 = line_one_top
                            p1.x3y3 = line_one_bottom

                            p1.refresh_coords()

                            p2.x1y1 = line_one_top
                            p2.x4y4 = line_one_bottom

                            line_two_top = (p2.x2y2[0] - x_movement,
                                            p2.x2y2[1])

                            line_two_bottom = (p2.x3y3[0] + x_movement,
                                               p2.x3y3[1])

                            p2.x2y2 = line_two_top
                            p2.x3y3 = line_two_bottom

                            p2.refresh_coords()

                            p3.x1y1 = line_two_top
                            p3.x4y4 = line_two_bottom

                            p3.refresh_coords()

                        else:

                            line_one_top = (p1.x2y2[0] + x_movement,
                                            p1.x2y2[1])

                            line_one_bottom = (p1.x3y3[0] - x_movement,
                                               p1.x3y3[1])

                            p1.x2y2 = line_one_top
                            p1.x3y3 = line_one_bottom

                            p1.refresh_coords()

                            p2.x1y1 = line_one_top
                            p2.x4y4 = line_one_bottom

                            line_two_top = (p2.x2y2[0] + x_movement,
                                            p2.x2y2[1])

                            line_two_bottom = (p2.x3y3[0] - x_movement,
                                               p2.x3y3[1])

                            p2.x2y2 = line_two_top
                            p2.x3y3 = line_two_bottom

                            p2.refresh_coords()

                            p3.x1y1 = line_two_top
                            p3.x4y4 = line_two_bottom

                            p3.refresh_coords()
                    else:
                        y_movement = min_height*(movement_proportion/100)

                        if rhombus_pattern == "right":

                            line_one_top = (p2.x2y2[0],
                                            p2.x2y2[1] + y_movement)

                            line_one_bottom = (p2.x1y1[0],
                                               p2.x1y1[1] - y_movement)

                            p2.x2y2 = line_one_top
                            p2.x1y1 = line_one_bottom

                            p1.x3y3 = line_one_top
                            p1.x4y4 = line_one_bottom

                            p1.refresh_coords()

                            line_two_top = (p2.x3y3[0],
                                            p2.x3y3[1] + y_movement)

                            line_two_bottom = (p2.x4y4[0],
                                               p2.x4y4[1] - y_movement)

                            p2.x3y3 = line_two_top
                            p2.x4y4 = line_two_bottom

                            p2.refresh_coords()

                            p3.x1y1 = line_two_bottom
                            p3.x2y2 = line_two_top

                            p3.refresh_coords()
                        else:

                            line_one_top = (p2.x2y2[0],
                                            p2.x2y2[1] - y_movement)

                            line_one_bottom = (p2.x1y1[0],
                                               p2.x1y1[1] + y_movement)

                            p2.x2y2 = line_one_top
                            p2.x1y1 = line_one_bottom

                            p1.x3y3 = line_one_top
                            p1.x4y4 = line_one_bottom

                            p1.refresh_coords()

                            line_two_top = (p2.x3y3[0],
                                            p2.x3y3[1] - y_movement)

                            line_two_bottom = (p2.x4y4[0],
                                               p2.x4y4[1] + y_movement)

                            p2.x3y3 = line_two_top
                            p2.x4y4 = line_two_bottom

                            p2.refresh_coords()

                            p3.x1y1 = line_two_bottom
                            p3.x2y2 = line_two_top

                            p3.refresh_coords()

    return page


def box_transform_page(page, direction_list=[]):
    """
    This function takes all the first child panels of a page
    and moves them to form a zigzag or a rhombus pattern

    :param page: Page to be transformed

    :type page: Page

    :param direction_list: A list of directions the page
    should move it's child panel's corner's to

    :return: Transformed page

    :rtype: Page
    """

    if len(page.children) > 1:

        # For all children of the page
        for idx in range(0, len(page.children)-1):

            # Take two children at a time
            p1 = page.get_child(idx)
            p2 = page.get_child(idx+1)

            change_proportion = np.random.randint(
                                    10,
                                    cfg.full_page_movement_proportion_limit
                                    )

            change_proportion /= 100

            # Randomly move the line between them up or down one side
            if len(direction_list) < 1:
                direction = np.random.choice(["rup", "lup"])
            else:
                direction = direction_list[idx]

            # If the first panel is horizontal therefore the second is too
            if p1.orientation == "h":

                # Get the maximum amount the line can move
                change_max = min([(p1.x4y4[1] - p1.x1y1[1]),
                                  (p2.x4y4[1] - p2.x1y1[1])])

                change = change_max*change_proportion

                # Specify the line to move
                line_top = p2.x1y1
                line_bottom = p2.x2y2

                # If the panel has children then recursively
                # find the leaf children and move them to the new line
                if len(p1.children) > 0:
                    move_children_to_line(p1,
                                          (line_top, line_bottom),
                                          change,
                                          "h",
                                          direction
                                          )

                # Otherwise move the current panels to line
                else:
                    if direction == "rup":
                        p1.x4y4 = (p1.x4y4[0], p1.x4y4[1] + change)
                        p1.refresh_coords()
                    else:
                        p1.x4y4 = (p1.x4y4[0], p1.x4y4[1] - change)
                        p1.refresh_coords()

                if len(p2.children) > 0:
                    move_children_to_line(p2,
                                          (line_top, line_bottom),
                                          change,
                                          "h",
                                          direction
                                          )
                else:
                    if direction == "rup":
                        p2.x1y1 = (p2.x1y1[0], p2.x1y1[1] + change)
                        p2.refresh_coords()
                    else:
                        p2.x1y1 = (p2.x1y1[0], p2.x1y1[1] - change)
                        p2.refresh_coords()

            # If the first panel is vertical therefore the second
            # is too since they are siblings
            else:
                # Get the maximum amount the line can move
                change_max = min([(p1.x2y2[0] - p1.x1y1[0]),
                                  (p2.x2y2[0] - p2.x1y1[0])])

                change = change_max*change_proportion

                # Specify the line to move
                line_top = p2.x1y1
                line_bottom = p2.x4y4

                # If the panel has children then recursively
                # find the leaf children and move them to the new line
                if len(p1.children) > 0:
                    move_children_to_line(p1,
                                          (line_top, line_bottom),
                                          change,
                                          "v",
                                          direction
                                          )

                # Otherwise just move the panel since it's a leaf
                else:
                    if direction == "rup":
                        p1.x2y2 = (p1.x2y2[0] - change, p1.x2y2[1])
                    else:
                        p1.x2y2 = (p1.x2y2[0] + change, p1.x2y2[1])

                if len(p2.children) > 0:
                    move_children_to_line(p2,
                                          (line_top, line_bottom),
                                          change,
                                          "v",
                                          direction
                                          )
                else:
                    if direction == "rup":
                        p2.x1y1 = (p2.x1y1[0] - change, p2.x1y1[1])
                    else:
                        p2.x1y1 = (p2.x1y1[0] + change, p2.x1y1[1])

    return page


def add_transforms(page):
    """Adds panel boundary transformations
    to the page

    :param page: Page to be transformed

    :type page: Page

    :return: Page with transformed panels

    :rtype: Page
    """
    # Transform types

    # Allow choosing multiple
    transform_choice = ["slice", "box"]

    # Slicing panels into multiple panels
    # Works best with large panels
    if "slice" in transform_choice:
        page = single_slice_panels(page)

        # Makes v cuts happen more often 1/4 chance
        if np.random.random() < cfg.double_slice_chance:
            page = single_slice_panels(page)

    if "box" in transform_choice:

        if np.random.random() < cfg.box_transform_panel_chance:
            page = box_transform_panels(page)

        page = box_transform_page(page)

    return page


def shrink_panels(page):
    """
    A function that uses the pyclipper library]
    to reduce the size of the panel polygon

    :param page: Page whose panels are to be
    shrunk

    :type page: Page

    :return: Page with shrunk panels

    :rtype: Page
    """

    panels = []
    if len(page.leaf_children) < 1:
        get_leaf_panels(page, panels)
        page.leaf_children = panels
    else:
        panels = page.leaf_children

    # For each panel
    for panel in panels:
        # Shrink them
        pco = pyclipper.PyclipperOffset()
        pco.AddPath(panel.get_polygon(),
                    pyclipper.JT_ROUND,
                    pyclipper.ET_CLOSEDPOLYGON
                    )

        solution = pco.Execute(cfg.panel_shrink_amount)

        # Get the solutions
        changed_coords = []
        if len(solution) > 0:
            for item in solution[0]:
                changed_coords.append(tuple(item))

            changed_coords.append(changed_coords[0])

            # Assign them
            panel.coords = changed_coords
            panel.x1y1 = changed_coords[0]
            panel.x2y2 = changed_coords[1]
            panel.x3y3 = changed_coords[2]
            panel.x4y4 = changed_coords[3]
        else:
            # Assign them as is if there are no solutions
            pass

    return page


def remove_panel(page):
    """
    This function randomly removes
    a panel from pages which have
    more than n+1 panels

    :param page: Page to remove panels from

    :type page: Page

    :return: Page with panels removed

    :rtype: Page
    """

    # If page has > n+1 children so there's
    # at least 1 panel left
    if page.num_panels > cfg.panel_removal_max + 1:

        # Remove 1 to n panels
        remove_number = np.random.choice([1, cfg.panel_removal_max])

        # Remove panel
        for i in range(remove_number):
            page.leaf_children.pop()

    return page


def add_background(page, image_dir, image_dir_path):
    """
    Add a background image to the page

    :param page: Page to add background to

    :type page: Page

    :param image_dir: A list of images

    :type image_dir: list

    :param image_dir_path: path to images used for adding
    the full path to the page

    :type image_dir_path: str

    :return: Page with background

    :rtype: Page
    """

    image_dir_len = len(image_dir)
    idx = np.random.randint(0, image_dir_len)
    page.background = image_dir_path + image_dir[idx]

    return page


# Page creators
def create_single_panel_metadata(panel,
                                 image_dir,
                                 image_dir_path,
                                 font_files,
                                 text_dataset,
                                 speech_bubble_files,
                                 speech_bubble_tags,
                                 minimum_speech_bubbles=0
                                 ):
    """
    This is a helper function that populates a single panel with
    an image, and a set of speech bubbles

    :param panel: Panel to add image and speech bubble to

    :type panel: Panel

    :param image_dir: List of images to pick from

    :type image_dir: list

    :param image_dir_path: Path of images dir to add to
    panels

    :type image_dir_path: str

    :param font_files: list of font files for speech bubble
    text

    :type font_files: list

    :param text_dataset: A dask dataframe of text to
    pick to render within speech bubble

    :type text_dataset: pandas.dataframe

    :param speech_bubble_files: list of base speech bubble
    template files

    :type speech_bubble_files: list

    :param speech_bubble_tags: a list of speech bubble
    writing area tags by filename

    :type speech_bubble_tags: list

    :param minimum_speech_bubbles: Set whether panels
    have a minimum number of speech bubbles, defaults to 0

    :type  minimum_speech_bubbles: int
    """

    # Image to be used inside panel
    image_dir_len = len(image_dir)
    select_image_idx = np.random.randint(0, image_dir_len)
    select_image = image_dir[select_image_idx]
    panel.image = image_dir_path+select_image

    # Select number of speech bubbles to assign to panel
    num_speech_bubbles = np.random.randint(minimum_speech_bubbles,
                                           cfg.max_speech_bubbles_per_panel)

    # Get lengths of datasets
    text_dataset_len = len(text_dataset)
    font_dataset_len = len(font_files)
    speech_bubble_dataset_len = len(speech_bubble_files)

    # Associated speech bubbles
    for speech_bubble in range(num_speech_bubbles):

        # Select a font
        font_idx = np.random.randint(0, font_dataset_len)
        font = font_files[font_idx]

        # Select a speech bubble and get it's writing areas
        speech_bubble_file_idx = np.random.randint(
                                    0,
                                    speech_bubble_dataset_len
                                    )

        speech_bubble_file = speech_bubble_files[speech_bubble_file_idx]

        area_idx = speech_bubble_tags['imagename'] == speech_bubble_file
        speech_bubble_writing_area = speech_bubble_tags[area_idx]['label']
        speech_bubble_writing_area = speech_bubble_writing_area.values[0]
        speech_bubble_writing_area = json.loads(speech_bubble_writing_area)

        # Select text for writing areas
        texts = []
        texts_indices = []
        for i in range(len(speech_bubble_writing_area)):
            text_idx = np.random.randint(0, text_dataset_len)
            texts_indices.append(text_idx)
            text = text_dataset.iloc[text_idx].to_dict()
            texts.append(text)

        # resize bubble to < 40% of panel area
        max_area = panel.area*cfg.bubble_to_panel_area_max_ratio
        new_area = np.random.random()*(max_area - max_area*0.375)
        new_area = max_area - new_area

        # Select location of bubble in panel
        width_m = np.random.random()
        height_m = np.random.random()

        xy = np.array(panel.coords)
        min_coord = np.min(xy[xy[:, 0] == np.min(xy[:, 0])], 0)

        x_choice = round(min_coord[0] + (panel.width//2 - 15)*width_m)
        y_choice = round(min_coord[1] + (panel.height//2 - 15)*height_m)

        location = [
            x_choice,
            y_choice
        ]

        speech_bubble_img = Image.open(speech_bubble_file)
        w, h = speech_bubble_img.size
        # Create speech bubble
        speech_bubble = SpeechBubble(texts=texts,
                                     text_indices=texts_indices,
                                     font=font,
                                     speech_bubble=speech_bubble_file,
                                     writing_areas=speech_bubble_writing_area,
                                     resize_to=new_area,
                                     location=location,
                                     width=w,
                                     height=h,
                                     )

        panel.speech_bubbles.append(speech_bubble)


def populate_panels(page,
                    image_dir,
                    image_dir_path,
                    font_files,
                    text_dataset,
                    speech_bubble_files,
                    speech_bubble_tags,
                    minimum_speech_bubbles=0
                    ):
    """
    This function takes all the panels and adds backgorund images
    and speech bubbles to them

    :param page: Page with panels to populate

    :type page: Page

    :param image_dir: List of images to pick from

    :type image_dir: list

    :param image_dir_path: Path of images dir to add to
    panels

    :type image_dir_path: str

    :param font_files: list of font files for speech bubble
    text

    :type font_files: list

    :param text_dataset: A dask dataframe of text to
    pick to render within speech bubble

    :type text_dataset: pandas.dataframe

    :param speech_bubble_files: list of base speech bubble
    template files

    :type speech_bubble_files: list

    :param speech_bubble_tags: a list of speech bubble
    writing area tags by filename

    :type speech_bubble_tags: list

    :param minimum_speech_bubbles: Set whether panels
    have a minimum number of speech bubbles, defaults to 0

    :type  minimum_speech_bubbles: int

    :return: Page with populated panels

    :rtype: Page
    """

    if page.num_panels > 1:
        for child in page.leaf_children:
            create_single_panel_metadata(child,
                                         image_dir,
                                         image_dir_path,
                                         font_files,
                                         text_dataset,
                                         speech_bubble_files,
                                         speech_bubble_tags,
                                         minimum_speech_bubbles
                                         )
    else:
        create_single_panel_metadata(page,
                                     image_dir,
                                     image_dir_path,
                                     font_files,
                                     text_dataset,
                                     speech_bubble_files,
                                     speech_bubble_tags,
                                     minimum_speech_bubbles
                                     )
    return page


def get_base_panels(num_panels=0,
                    layout_type=None,
                    type_choice=None,
                    page_name=None):
    """
    This function creates the base panels for one page
    it specifies how a page should be layed out and
    how many panels should be in it

    :param num_panels: how many panels should be on a page
    if 0 then the function chooses, defaults to 0

    :type num_panels: int, optional

    :param layout_type: whether the page should consist of
    vertical, horizontal or both types of panels, defaults to None

    :type layout_type: str, optional

    :param type_choice: If having selected vh panels select a type
    of layout specifically, defaults to None

    :type type_choice: str, optional

    :param page_name: A specific name for the page

    :type page_name: str, optional

    :return: A Page object with the panels initalized

    :rtype: Page
    """

    # TODO: Skew panel number distribution

    # Page dimensions turned to coordinates
    topleft = (0.0, 0.0)
    topright = (cfg.page_width, 0.0)
    bottomleft = (0.0, cfg.page_height)
    bottomright = cfg.page_size
    coords = [
        topleft,
        topright,
        bottomright,
        bottomleft
    ]

    if layout_type is None:
        layout_type = np.random.choice(["v", "h", "vh"])

    # Panels encapsulated and returned within page
    if page_name is None:
        page = Page(coords, layout_type, num_panels)
    else:
        page = Page(coords, layout_type, num_panels, name=page_name)

    # If you want only vertical panels
    if layout_type == "v":
        max_num_panels = 4
        if num_panels < 1:
            num_panels = np.random.choice([3, 4])
            page.num_panels = num_panels
        else:
            page.num_panels = num_panels

        draw_n_shifted(num_panels, page, "v")

    # If you want only horizontal panels
    elif layout_type == "h":
        max_num_panels = 5
        if num_panels < 1:
            num_panels = np.random.randint(3, max_num_panels+1)
            page.num_panels = num_panels
        else:
            page.num_panels = num_panels

        draw_n_shifted(num_panels, page, "h")

    # If you want both horizontal and vertical panels
    elif layout_type == "vh":

        max_num_panels = 8
        if num_panels < 1:
            num_panels = np.random.randint(2, max_num_panels+1)
            page.num_panels = num_panels
        else:
            page.num_panels = num_panels

        if num_panels == 2:
            # Draw 2 rectangles
            # vertically or horizontally
            horizontal_vertical = np.random.choice(["h", "v"])
            draw_two_shifted(page, horizontal_vertical)

        if num_panels == 3:
            # Draw 2 rectangles
            # Vertically or Horizontally

            horizontal_vertical = np.random.choice(["h", "v"])
            draw_two_shifted(page, horizontal_vertical)

            next_div = invert_for_next(horizontal_vertical)

            # Pick one and divide it into 2 rectangles
            choice_idx = choose(page)
            choice = page.get_child(choice_idx)

            draw_two_shifted(choice, next_div)

        if num_panels == 4:
            horizontal_vertical = np.random.choice(["h", "v"])

            # Possible layouts with 4 panels
            if type_choice is None:
                type_choice = np.random.choice(["eq", "uneq", "div",
                                                "trip", "twoonethree"])

            # Draw two rectangles
            if type_choice == "eq":
                draw_two_shifted(page, horizontal_vertical, shift=0.5)
                next_div = invert_for_next(horizontal_vertical)

                # Divide each into 2 rectangles equally
                shift_min = 25
                shift_max = 75
                shift = np.random.randint(shift_min, shift_max)
                shift = shift/100

                draw_two_shifted(page.get_child(0), next_div, shift)
                draw_two_shifted(page.get_child(1), next_div, shift)

            # Draw two rectangles
            elif type_choice == "uneq":
                draw_two_shifted(page, horizontal_vertical, shift=0.5)
                next_div = invert_for_next(horizontal_vertical)

                # Divide each into 2 rectangles unequally
                draw_two_shifted(page.get_child(0), next_div)
                draw_two_shifted(page.get_child(1), next_div)

            elif type_choice == "div":
                draw_two_shifted(page, horizontal_vertical, shift=0.5)
                next_div = invert_for_next(horizontal_vertical)

                # Pick one and divide into 2 rectangles
                choice1_idx = choose(page)
                choice1 = page.get_child(choice1_idx)

                draw_two_shifted(choice1, next_div)

                # Pick one of these two and divide that into 2 rectangles
                choice2_idx = choose(choice1)
                choice2 = choice1.get_child(choice2_idx)

                next_div = invert_for_next(next_div)
                draw_two_shifted(choice2, next_div)

            # Draw three rectangles
            elif type_choice == "trip":
                draw_n(3, page, horizontal_vertical)

                # Pick one and divide it into two
                choice_idx = choose(page)
                choice = page.get_child(choice_idx)

                next_div = invert_for_next(horizontal_vertical)

                draw_two_shifted(choice, next_div)

            # Draw two rectangles
            elif type_choice == "twoonethree":

                draw_two_shifted(page, horizontal_vertical)

                # Pick one and divide it into 3 rectangles
                choice_idx = choose(page)
                choice = page.get_child(choice_idx)

                next_div = invert_for_next(horizontal_vertical)

                draw_n_shifted(3, choice, next_div)

        if num_panels == 5:

            # Draw two rectangles
            horizontal_vertical = np.random.choice(["h", "v"])

            # Possible layouts with 5 panels
            if type_choice is None:
                type_choice = np.random.choice(["eq", "uneq", "div",
                                                "twotwothree", "threetwotwo",
                                                "fourtwoone"])

            if type_choice == "eq" or type_choice == "uneq":

                draw_two_shifted(page, horizontal_vertical, shift=0.5)
                next_div = invert_for_next(horizontal_vertical)

                # Pick one and divide it into two then
                choice_idx = choose(page)
                choice = page.get_child(choice_idx)

                draw_two_shifted(choice, next_div)

                # Divide each into 2 rectangles equally
                if type_choice == "eq":
                    shift_min = 25
                    shift_max = 75
                    shift = np.random.randint(shift_min, shift_max)
                    set_shift = shift/100
                else:
                    # Divide each into 2 rectangles unequally
                    set_shift = None

                next_div = invert_for_next(next_div)
                draw_two_shifted(choice.get_child(0),
                                 next_div,
                                 shift=set_shift)

                draw_two_shifted(choice.get_child(1),
                                 next_div,
                                 shift=set_shift)

            # Draw two rectangles
            elif type_choice == "div":
                draw_two_shifted(page, horizontal_vertical, shift=0.5)
                next_div = invert_for_next(horizontal_vertical)

                # Divide both equally
                draw_two_shifted(page.get_child(0), next_div)
                draw_two_shifted(page.get_child(1), next_div)

                # Pick one of all of them and divide into two
                page_child_chosen = np.random.choice(page.children)
                choice_idx, left_choices = choose_and_return_other(
                                                    page_child_chosen
                                                    )

                choice = page_child_chosen.get_child(choice_idx)

                next_div = invert_for_next(next_div)
                draw_two_shifted(choice,
                                 horizontal_vertical=next_div,
                                 shift=0.5
                                 )

            # Draw two rectangles
            elif type_choice == "twotwothree":

                draw_two_shifted(page, horizontal_vertical, shift=0.5)
                next_div = invert_for_next(horizontal_vertical)

                # Pick which one gets 2 and which gets 3
                choice_idx, left_choices = choose_and_return_other(page)
                choice = page.get_child(choice_idx)
                other = page.get_child(left_choices[0])

                # Divide one into 2
                next_div = invert_for_next(horizontal_vertical)
                draw_two_shifted(choice, next_div)

                # Divide other into 3
                draw_n(3, other, next_div)

            # Draw 3 rectangles (horizontally or vertically)
            elif type_choice == "threetwotwo":

                draw_n(3, page, horizontal_vertical)
                next_div = invert_for_next(horizontal_vertical)

                choice1_idx, left_choices = choose_and_return_other(page)
                choice2_idx = np.random.choice(left_choices)
                choice1 = page.get_child(choice1_idx)
                choice2 = page.get_child(choice2_idx)

                # Pick two and divide each into two
                draw_two_shifted(choice1, next_div)
                draw_two_shifted(choice2, next_div)

            # Draw 4 rectangles vertically
            elif type_choice == "fourtwoone":
                draw_n(4, page, horizontal_vertical)

                # Pick one and divide into two
                choice_idx = choose(page)
                choice = page.get_child(choice_idx)

                next_div = invert_for_next(horizontal_vertical)
                draw_two_shifted(choice, next_div)

        if num_panels == 6:

            # Possible layouts with 6 panels
            if type_choice is None:
                type_choice = np.random.choice(["tripeq", "tripuneq",
                                                "twofourtwo", "twothreethree",
                                                "fourtwotwo"])

            horizontal_vertical = np.random.choice(["v", "h"])

            # Draw 3 rectangles (V OR H)
            if type_choice == "tripeq" or type_choice == "tripuneq":
                draw_n_shifted(3, page, horizontal_vertical)
                # Split each equally
                if type_choice == "tripeq":
                    shift = np.random.randint(25, 75)
                    shift = shift/100
                # Split each unequally
                else:
                    shift = None

                next_div = invert_for_next(horizontal_vertical)
                for panel in page.children:
                    draw_two_shifted(panel, next_div, shift=shift)

            # Draw 2 rectangles
            elif type_choice == "twofourtwo":
                draw_two_shifted(page, horizontal_vertical)
                # Split into 4 one half 2 in another
                next_div = invert_for_next(horizontal_vertical)
                draw_n_shifted(4, page.get_child(0), next_div)
                draw_two_shifted(page.get_child(1), next_div)

            # Draw 2 rectangles
            elif type_choice == "twothreethree":
                # Split 3 in each
                draw_two_shifted(page, horizontal_vertical)
                next_div = invert_for_next(horizontal_vertical)

                for panel in page.children:
                    # Allow each inital panel to grow to up to 75% of 100/n
                    n = 3
                    shifts = []
                    choice_max = round((100/n)*1.5)
                    choice_min = round((100/n)*0.5)
                    for i in range(0, n):
                        shift_choice = np.random.randint(
                                                choice_min,
                                                choice_max
                                                )

                        choice_max = choice_max + ((100/n) - shift_choice)
                        shifts.append(shift_choice)

                    to_add_or_remove = (100 - sum(shifts))/len(shifts)

                    normalized_shifts = []
                    for shift in shifts:
                        new_shift = shift + to_add_or_remove
                        normalized_shifts.append(new_shift/100)

                    draw_n_shifted(3,
                                   panel,
                                   next_div,
                                   shifts=normalized_shifts
                                   )

            # Draw 4 rectangles
            elif type_choice == "fourtwotwo":
                draw_n_shifted(4, page, horizontal_vertical)

                # Split two of them
                choice1_idx, left_choices = choose_and_return_other(page)
                choice2_idx = np.random.choice(left_choices)
                choice1 = page.get_child(choice1_idx)
                choice2 = page.get_child(choice2_idx)

                next_div = invert_for_next(horizontal_vertical)
                draw_two_shifted(choice1, next_div)
                draw_two_shifted(choice2, next_div)

        if num_panels == 7:

            # Possible layouts with 7 panels
            types = ["twothreefour", "threethreetwotwo", "threefourtwoone",
                     "threethreextwoone", "fourthreextwo"]

            if type_choice is None:
                type_choice = np.random.choice(types)

            # Draw two split 3-4 - HV
            # Draw two rectangles
            if type_choice == "twothreefour":
                horizontal_vertical = np.random.choice(["h", "v"])

                draw_two_shifted(page, horizontal_vertical, shift=0.5)

                # Pick one and split one into 4 rectangles
                choice_idx, left_choices = choose_and_return_other(page)
                choice = page.get_child(choice_idx)
                other = page.get_child(left_choices[0])

                next_div = invert_for_next(horizontal_vertical)

                draw_n_shifted(4, choice, next_div)

                # Some issue with the function calls and seeding
                n = 3
                shifts = []
                choice_max = round((100/n)*1.5)
                choice_min = round((100/n)*0.5)
                for i in range(0, n):
                    shift_choice = np.random.randint(choice_min, choice_max)
                    choice_max = choice_max + ((100/n) - shift_choice)
                    shifts.append(shift_choice)

                to_add_or_remove = (100 - sum(shifts))/len(shifts)

                normalized_shifts = []
                for shift in shifts:
                    new_shift = shift + to_add_or_remove
                    normalized_shifts.append(new_shift/100)

                # Pick another and split into 3 rectangles
                draw_n_shifted(3, other, next_div, shifts=normalized_shifts)

            # Draw three rectangles
            elif type_choice == "threethreetwotwo":
                draw_n(3, page, "h")

                # Pick one and split it into 3 rectangles
                choice_idx, left_choices = choose_and_return_other(page)
                choice = page.get_child(choice_idx)

                draw_n_shifted(3, choice, "v")

                # Split the other two into 2 rectangles
                draw_two_shifted(page.get_child(left_choices[0]), "v")
                draw_two_shifted(page.get_child(left_choices[1]), "v")

            # Draw 3 rectangles
            elif type_choice == "threefourtwoone":
                draw_n(3, page, "h")

                # Pick two of three rectangles and let one be
                choice_idx, left_choices = choose_and_return_other(page)
                choice = page.get_child(choice_idx)
                other_idx = np.random.choice(left_choices)
                other = page.get_child(other_idx)

                # Of the picked split one into 4 rectangles
                draw_n_shifted(4, choice, "v")

                # Split the other into 2 rectangles
                draw_two_shifted(other, "v")

            # Draw 3 rectangles
            elif type_choice == "threethreextwoone":

                draw_n(3, page, "h")

                # Pick two and leave one
                choice_idx, left_choices = choose_and_return_other(page)
                choice = page.get_child(choice_idx)
                other = page.get_child(left_choices[0])

                # Of the picked split one into 3
                draw_n_shifted(3, choice, "v")

                # Some issue with the function calls and seeding
                n = 3
                shifts = []
                choice_max = round((100/n)*1.5)
                choice_min = round((100/n)*0.5)
                for i in range(0, n):
                    shift_choice = np.random.randint(choice_min, choice_max)
                    choice_max = choice_max + ((100/n) - shift_choice)
                    shifts.append(shift_choice)

                to_add_or_remove = (100 - sum(shifts))/len(shifts)

                normalized_shifts = []
                for shift in shifts:
                    new_shift = shift + to_add_or_remove
                    normalized_shifts.append(new_shift/100)

                # Split the other into 3 as well
                draw_n_shifted(3, other, "v", shifts=normalized_shifts)

            # Draw 4 split 3x2 - HV

            # Draw 4 rectangles
            elif type_choice == "fourthreextwo":
                horizontal_vertical = np.random.choice(["h", "v"])
                draw_n(4, page, horizontal_vertical)

                # Choose one and leave as is
                choice_idx, left_choices = choose_and_return_other(page)

                # Divide the rest into two
                next_div = invert_for_next(horizontal_vertical)
                for panel in left_choices:
                    draw_two_shifted(page.get_child(panel), next_div)

        if num_panels == 8:

            # Possible layouts for 8 panels
            types = ["fourfourxtwoeq", "fourfourxtwouneq",
                     "threethreethreetwo", "threefourtwotwo",
                     "threethreefourone"]

            if type_choice is None:
                type_choice = np.random.choice(types)

            # Draw 4 rectangles
            # equal or uneqal 4-4x2
            if type_choice == types[0] or type_choice == types[1]:
                # panels = draw_n_shifted(4, *coords, "h")
                draw_n(4, page, "h")
                # Equal
                if type_choice == "fourfourxtwoeq":
                    shift_min = 25
                    shift_max = 75
                    shift = np.random.randint(shift_min, shift_max)
                    set_shift = shift/100
                # Unequal
                else:
                    set_shift = None

                # Drivide each into two
                for panel in page.children:

                    draw_two_shifted(panel, "v", shift=set_shift)

            # Where three rectangles need to be drawn
            if type_choice in types[2:]:
                draw_n(3, page, "h")

                # Draw 3 rectangles then
                if type_choice == "threethreethreetwo":

                    # Choose one and divide it into two
                    choice_idx, left_choices = choose_and_return_other(page)
                    choice = page.get_child(choice_idx)
                    draw_two_shifted(choice, "v")

                    # Divide the rest into 3
                    for panel in left_choices:
                        # Some issue with the function calls and seeding
                        n = 3
                        shifts = []
                        choice_max = round((100/n)*1.5)
                        choice_min = round((100/n)*0.5)
                        for i in range(0, n):
                            shift_choice = np.random.randint(
                                            choice_min,
                                            choice_max
                                            )

                            choice_max = choice_max + ((100/n) - shift_choice)
                            shifts.append(shift_choice)

                        to_add_or_remove = (100 - sum(shifts))/len(shifts)

                        normalized_shifts = []
                        for shift in shifts:
                            new_shift = shift + to_add_or_remove
                            normalized_shifts.append(new_shift/100)

                        draw_n_shifted(3,
                                       page.get_child(panel),
                                       "v",
                                       shifts=normalized_shifts
                                       )

                # Draw 3 rectangles then
                elif type_choice == "threefourtwotwo":

                    # Choosen one and divide it into 4
                    choice_idx, left_choices = choose_and_return_other(page)
                    choice = page.get_child(choice_idx)

                    draw_n_shifted(4, choice, "v")

                    for panel in left_choices:
                        draw_two_shifted(page.get_child(panel), "v")

                # Draw 3 3-4-1 - H

                # Draw three rectangles then
                elif type_choice == "threethreefourone":

                    # Choose two and leave one as is
                    choice_idx, left_choices = choose_and_return_other(page)
                    choice = page.get_child(choice_idx)
                    other_idx = np.random.choice(left_choices)
                    other = page.get_child(other_idx)

                    # Divide one into 3 rectangles
                    draw_n_shifted(3, choice, "v")

                    # Some issue with the function calls and seeding
                    n = 4
                    shifts = []
                    choice_max = round((100/n)*1.5)
                    choice_min = round((100/n)*0.5)
                    for i in range(0, n):
                        shift_choice = np.random.randint(
                                            choice_min,
                                            choice_max
                                            )

                        choice_max = choice_max + ((100/n) - shift_choice)
                        shifts.append(shift_choice)

                    to_add_or_remove = (100 - sum(shifts))/len(shifts)

                    normalized_shifts = []
                    for shift in shifts:
                        new_shift = shift + to_add_or_remove
                        normalized_shifts.append(new_shift/100)

                    # Divide the other into 4 rectangles
                    draw_n_shifted(4, other, "v", shifts=normalized_shifts)

    return page


def create_page_metadata(image_dir,
                         image_dir_path,
                         font_files,
                         text_dataset,
                         speech_bubble_files,
                         speech_bubble_tags):
    """
    This function creates page metadata for a single page. It includes
    transforms, background addition, random panel removal,
    panel shrinking, and the populating of panels with
    images and speech bubbles.

    :param image_dir: List of images to pick from

    :type image_dir: list

    :param image_dir_path: Path of images dir to add to
    panels

    :type image_dir_path: str

    :param font_files: list of font files for speech bubble
    text

    :type font_files: list

    :param text_dataset: A dask dataframe of text to
    pick to render within speech bubble

    :type text_dataset: pandas.dataframe

    :param speech_bubble_files: list of base speech bubble
    template files

    :type speech_bubble_files: list

    :param speech_bubble_tags: a list of speech bubble
    writing area tags by filename

    :type speech_bubble_tags: list

    :return: Created Page with all the bells and whistles

    :rtype: Page
    """

    # Select page type
    page_type = np.random.choice(
        list(cfg.vertical_horizontal_ratios.keys()),
        p=list(cfg.vertical_horizontal_ratios.values())
    )

    # Select number of panels on the page
    # between 1 and 8

    number_of_panels = np.random.choice(
        list(cfg.num_pages_ratios.keys()),
        p=list(cfg.num_pages_ratios.values())
    )

    page = get_base_panels(number_of_panels, page_type)

    if np.random.random() < cfg.panel_transform_chance:
        page = add_transforms(page)

    page = shrink_panels(page)
    page = populate_panels(page,
                           image_dir,
                           image_dir_path,
                           font_files,
                           text_dataset,
                           speech_bubble_files,
                           speech_bubble_tags
                           )

    if np.random.random() < cfg.panel_removal_chance:
        page = remove_panel(page)

    if number_of_panels == 1:
        page = add_background(page, image_dir, image_dir_path)
    else:
        if np.random.random() < cfg.background_add_chance:
            page = add_background(page, image_dir, image_dir_path)

    return page
