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
from .helpers import invert_for_next, choose, choose_and_return_other, get_min_area_panels, get_leaf_panels, find_parent_with_multiple_children, move_children_to_line
from .. import config_file as cfg

# Creation helpers
def draw_n_shifted(n, parent, horizontal_vertical, shifts=[]):
    """
    A function to take a parent Panel and divide it into n
    sub-panel's vertically or horizontally with each panels having
    specified size ratios along the axis perpendicular to their orientation

    :param n: Number of sub-panels
    
    :type int:

    :param parent: The parent panel being split
    
    :type Panel:

    :param horizontal_vertical: Whether to render the sub-panels vertically
    or horizontally in regards to the page

    :type str:

    :param shifts: Ratios to divide the panel into sub-panels

    :type list:
    """

    # Specify panel dimensions
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
            
            # If not it has the same top side as it's previous sibiling's bottom side
            else:
                # this shift level is the same as the bottom side of the sibling panel
                shift_level += normalized_shifts[i-1]

                # Specify points for the top side
                x1y1 = (bottomleft[0], topleft[1] + (bottomleft[1] - topleft[1])*shift_level)
                x2y2 = (bottomright[0], topright[1] + (bottomright[1]- topright[1])*shift_level)

            # If it's the last panel then it has the
            # same right side as the parent bottom side
            if i == (n-1):
                x3y3 = bottomright
                x4y4 = bottomleft
            
            # If not it has the same bottom side as it's next sibling's top side 
            else:
                # Same shift level as the left side of next sibling
                next_shift_level = shift_level + normalized_shifts[i]

                # Specify points for the bottom side
                x3y3 = (bottomright[0], topright[1] + (bottomright[1]- topright[1])*next_shift_level)
                x4y4 = (bottomleft[0], topleft[1] + (bottomleft[1] - topleft[1])*next_shift_level)

            # Create a Panel
            poly_coords = (x1y1, x2y2, x3y3, x4y4)
            poly = Panel(poly_coords, parent.name+"-"+str(i), orientation=horizontal_vertical, parent=parent, children=[])
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
            
            # if not it's left side is the same as it's sib
            else:
                shift_level += normalized_shifts[i-1]
                x1y1 = (topleft[0] + (topright[0] - topleft[0])*shift_level, topright[1])
                x4y4 = (bottomleft[0] + (bottomright[0] - bottomleft[0])*shift_level, bottomright[1])

            if i == (n-1):
                x2y2 = topright
                x3y3 = bottomright
            else:
                next_shift_level = shift_level + normalized_shifts[i]
                x2y2 = (topleft[0] + (topright[0] - topleft[0])*next_shift_level, topright[1])
                x3y3 = (bottomleft[0] + (bottomright[0] - bottomleft[0])*next_shift_level, bottomright[1])

            poly_coords = (x1y1, x2y2, x3y3, x4y4)
            poly = Panel(poly_coords, parent.name+"-"+str(i), orientation=horizontal_vertical, parent=parent, children=[])
            parent.add_child(poly)

def draw_n(n, parent, horizontal_vertical):

        topleft = parent.x1y1
        topright = parent.x2y2
        bottomright = parent.x3y3
        bottomleft = parent.x4y4
        
        if horizontal_vertical == "h":
            for i in range(0, n):
                if i == 0:
                    x1y1 = topleft
                    x2y2 = topright
                else:
                   x1y1 = (bottomleft[0], topleft[1] + (bottomleft[1] - topleft[1])*(i/n))
                   x2y2 = (bottomright[0], topright[1] + (bottomright[1]- topright[1])*(i/n))
                
                if i == (n-1):
                    x3y3 = bottomright
                    x4y4 = bottomleft
                else:
                    x3y3 = (bottomright[0], topright[1] + (bottomright[1]- topright[1])*((i+1)/n))
                    x4y4 = (bottomleft[0], topleft[1] + (bottomleft[1] - topleft[1])*((i+1)/n))

                poly_coords = (x1y1, x2y2, x3y3, x4y4)
                poly = Panel(poly_coords, parent.name+"-"+str(i), orientation=horizontal_vertical, parent=parent, children=[])
                parent.add_child(poly)
        
        if horizontal_vertical == "v":
            for i in range(0, n):

                if i == 0:
                    x1y1 = topleft
                    x4y4 = bottomleft 
                else:
                    x1y1 = (topleft[0] + (topright[0] - topleft[0])*(i/n), topright[1])
                    x4y4 = (bottomleft[0] + (bottomright[0] - bottomleft[0])*(i/n), bottomright[1])

                if i == (n-1):
                    x2y2 = topright
                    x3y3 = bottomright
                else:
                    x2y2 = (topleft[0] + (topright[0] - topleft[0])*((i+1)/n), topright[1])
                    x3y3 = (bottomleft[0] + (bottomright[0] - bottomleft[0])*((i+1)/n), bottomright[1])

                poly_coords = (x1y1, x2y2, x3y3, x4y4)
                poly = Panel(poly_coords, parent.name+"-"+str(i), orientation=horizontal_vertical, parent=parent, children=[])
                parent.add_child(poly)

def draw_two_shifted(parent, horizontal_vertical, shift=None):

    topleft = parent.x1y1
    topright = parent.x2y2
    bottomright = parent.x3y3
    bottomleft = parent.x4y4

    if shift is None:
        shift_min = 25
        shift_max = 75
        shift = np.random.randint(shift_min, shift_max)
        shift = shift/100

    if horizontal_vertical == "h":
        r1x1y1 = topleft
        r1x2y2 = topright
        r1x3y3 = (bottomright[0], topright[1] + (bottomright[1] - topright[1])*shift)
        r1x4y4 = (bottomleft[0], topleft[1] + (bottomleft[1] - topleft[1])*shift)

        poly1_coords = (r1x1y1, r1x2y2, r1x3y3, r1x4y4)

        r2x1y1 = (bottomleft[0], topleft[1] + (bottomleft[1] - topleft[1])*shift)
        r2x2y2 = (bottomright[0], topright[1] + (bottomright[1] - topright[1])*shift)
        r2x3y3 = bottomright
        r2x4y4 = bottomleft

        poly2_coords = (r2x1y1, r2x2y2, r2x3y3, r2x4y4, r2x1y1)

        poly1 = Panel(poly1_coords, parent.name + "-0", orientation=horizontal_vertical, parent=parent, children=[])
        poly2 = Panel(poly2_coords, parent.name + "-1", orientation=horizontal_vertical, parent=parent, children=[])

        parent.add_children([poly1, poly2])
    
    if horizontal_vertical == "v":
        
        r1x1y1 = topleft
        r1x2y2 = (topleft[0] + (topright[0] - topleft[0])*shift, topright[1])
        r1x3y3 = (bottomleft[0] + (bottomright[0] - bottomleft[0])*shift, bottomright[1])
        r1x4y4 = bottomleft

        poly1_coords = (r1x1y1, r1x2y2, r1x3y3, r1x4y4, r1x1y1)

        r2x1y1 = (topleft[0] + (topright[0] - topleft[0])*shift, topright[1])
        r2x2y2 = topright
        r2x3y3 = bottomright
        r2x4y4 = (bottomleft[0] + (bottomright[0] - bottomleft[0])*shift, bottomright[1])

        poly2_coords = (r2x1y1, r2x2y2, r2x3y3, r2x4y4, r2x1y1)

        poly1 = Panel(poly1_coords, parent.name + "-0", orientation=horizontal_vertical, parent=parent, children=[])
        poly2 = Panel(poly2_coords, parent.name + "-1", orientation=horizontal_vertical, parent=parent, children=[])

        parent.add_children([poly1, poly2])

# Page transformations
def single_slice_panels(page, type_choice=None):

    # Remove panels which are too small 
    relevant_panels = [] 
    get_min_area_panels(page, 0.2, ret_panels=relevant_panels) 

    # Shuffle panels for randomness
    random.shuffle(relevant_panels)

    # single slice close
    if type_choice == None:
        type_choice =  np.random.choice(["center", "side"])

    type_choice = "center"
    num_panels_added = 0
    # Center
    # TODO: Remember to add number of panels increase to page 
    if type_choice == "center":
        if len(relevant_panels) < 1:
            return page

        if len(relevant_panels) > 1:
            number_to_slice = np.random.randint(1, len(relevant_panels))
        else:
            number_to_slice = 1
        
        for idx in range(0, number_to_slice):
            panel = relevant_panels[idx]
            num_panels_added += 1

            # Decide which direction to cut in
            horizontal_vertical = np.random.choice(["h", "v"])

            # Get center line
            # Vertical slice
            if horizontal_vertical == "v":
                panel_chosen_coord_length = (panel.x2y2[0] - panel.x1y1[0])/2

                # Slice panel
                draw_n(2, panel, "v")

                # Skew it left or right
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

                    p1.coords[1] = p1.x2y2
                    p1.coords[2] = p1.x3y3

                    p2.x1y1 = (p2.x1y1[0] - skew_amount, p2.x1y1[1])
                    p2.x4y4 = (p2.x4y4[0] + skew_amount, p2.x4y4[1])

                    p2.coords[0] = p2.x1y1
                    p2.coords[3] = p2.x4y4

                else:
                    p1.x2y2 = (p1.x2y2[0] + skew_amount, p1.x2y2[1])
                    p1.x3y3 = (p1.x3y3[0] - skew_amount, p1.x3y3[1])

                    p1.coords[1] = p1.x2y2
                    p1.coords[2] = p1.x3y3

                    p2.x1y1 = (p2.x1y1[0] + skew_amount, p2.x1y1[1])
                    p2.x4y4 = (p2.x4y4[0] - skew_amount, p2.x4y4[1])

                    p2.coords[0] = p2.x1y1
                    p2.coords[3] = p2.x4y4
            # Horizontal slice
            else:
                panel_chosen_coord_length = (panel.x3y3[1] - panel.x2y2[1])/2

                # Slice panel
                draw_n(2, panel, "h")

                # Skew it left or right
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

                    p1.coords[2] = p1.x3y3
                    p1.coords[3] = p1.x4y4

                    p2.x1y1 = (p2.x1y1[0], p2.x1y1[1] + skew_amount)
                    p2.x2y2 = (p2.x2y2[0], p2.x2y2[1] - skew_amount)

                    p2.coords[0] = p2.x1y1
                    p2.coords[1] = p2.x2y2

                else:
                    p1.x4y4 = (p1.x4y4[0], p1.x4y4[1] - skew_amount)
                    p1.x3y3 = (p1.x3y3[0], p1.x3y3[1] + skew_amount)

                    p1.coords[2] = p1.x3y3
                    p1.coords[3] = p1.x4y4

                    p2.x1y1 = (p2.x1y1[0], p2.x1y1[1] - skew_amount)
                    p2.x2y2 = (p2.x2y2[0], p2.x2y2[1] + skew_amount)

                    p2.coords[0] = p2.x1y1
                    p2.coords[1] = p2.x2y2
    # Sides
    # TODO: Add multiple sides by refactoring Panel to be fully polygon
    else:
        if len(relevant_panels) < 1:
            return page

        if len(relevant_panels) > 1:
            number_to_slice = np.random.choice([1, 3])
        else:
            number_to_slice = 1

        for panel in relevant_panels[0:number_to_slice]:                
            side = np.random.choice(["tr", "tl", "br", "bl"])

            draw_n(2, panel, "h")
            num_panels_added += 1

            p1 = panel.get_child(0)
            p2 = panel.get_child(1)

            # Panels are non standard polygons
            p1.non_rect = True
            p2.non_rect = True

            p1.sliced = True
            p2.sliced = True

            cut_y_proportion = np.random.randint(30, 75)/100
            cut_x_proportion = np.random.randint(30, 75)/100
            cut_y_length = (panel.x4y4[1] - panel.x1y1[1])*cut_y_proportion
            cut_x_length = (panel.x3y3[0] - panel.x4y4[0])*cut_x_proportion

            # bottom left corner
            if side == "bl":

                p1_cut_x1y1 = (panel.x4y4[0], panel.x4y4[1] - cut_y_length)
                p1_cut_x2y2 = (panel.x4y4[0] + cut_x_length, panel.x4y4[1])
                p1_cut_x3y3 = (panel.x4y4)

                p1.coords = [p1_cut_x1y1, p1_cut_x2y2, p1_cut_x3y3, p1_cut_x1y1]

                p2.coords = [panel.x1y1, panel.x2y2, panel.x3y3, p1_cut_x2y2, p1_cut_x1y1, panel.x1y1] 
            
            # bottom right corner
            elif side == "br":

                p1_cut_x1y1 = (panel.x3y3[0], panel.x3y3[1] - cut_y_length)
                p1_cut_x2y2 = (panel.x3y3)
                p1_cut_x3y3 = (panel.x3y3[0] - cut_x_length, panel.x3y3[1])

                p1.coords = [p1_cut_x1y1, p1_cut_x2y2, p1_cut_x3y3, p1_cut_x1y1]
                p2.coords = [panel.x1y1, panel.x2y2, p1_cut_x1y1, p1_cut_x3y3, panel.x4y4, panel.x1y1] 

            # top left corner 
            elif side == "tl":

                p1_cut_x1y1 = panel.x1y1
                p1_cut_x2y2 = (panel.x1y1[0] + cut_x_length, panel.x1y1[1])
                p1_cut_x3y3 = (panel.x1y1[0], panel.x1y1[1] + cut_y_length)

                p1.coords = [p1_cut_x1y1, p1_cut_x2y2, p1_cut_x3y3, p1_cut_x1y1]
                p2.coords = [p1_cut_x2y2, panel.x2y2, panel.x3y3, panel.x4y4, p1_cut_x3y3, p1_cut_x1y1] 

            # top right corner
            else:
                p1_cut_x1y1 = (panel.x2y2[0] - cut_x_length, panel.x2y2[1])
                p1_cut_x2y2 = panel.x2y2 
                p1_cut_x3y3 = (panel.x2y2[0], panel.x2y2[1] + cut_y_length)

                p1.coords = [p1_cut_x1y1, p1_cut_x2y2, p1_cut_x3y3, p1_cut_x1y1]
                p2.coords = [panel.x1y1, p1_cut_x1y1, p1_cut_x3y3, panel.x3y3, panel.x4y4, panel.x1y1]

    page.num_panels +=  num_panels_added

    return page

def box_transform_panels(page, type_choice=None):

    if type_choice == None:
        type_choice = np.random.choice(["trapezoid", "rhombus"])

    if type_choice == "trapezoid":
        if page.num_panels > 2:
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

                    for child in [p1, p2, p3]:

                        if child.width < min_width:
                            min_width = child.width
                        
                        if child.height < min_height:
                            min_height = child.height

                    trapezoid_pattern = np.random.choice(["A", "V"])

                    movement_proportion = np.random.randint(10, 50)

                    if panel.orientation == "h":
                        
                        x_movement = min_width*(movement_proportion/100)

                        if trapezoid_pattern == "A":
                            line_one_top = (p1.x2y2[0] + x_movement, p1.x2y2[1])
                            line_one_bottom = (p1.x3y3[0] - x_movement, p1.x3y3[1])

                            p1.x2y2 = line_one_top
                            p1.x3y3 = line_one_bottom

                            p2.x1y1 = line_one_top
                            p2.x4y4 =line_one_bottom 

                            line_two_top = (p2.x2y2[0] - x_movement, p2.x2y2[1])
                            line_two_bottom = (p2.x3y3[0] + x_movement, p2.x3y3[1])

                            p2.x2y2 = line_two_top
                            p2.x3y3 = line_two_bottom

                            p3.x1y1 = line_two_top
                            p3.x4y4 = line_two_bottom 
                        
                        else:

                            line_one_top = (p1.x2y2[0] - x_movement, p1.x2y2[1])
                            line_one_bottom = (p1.x3y3[0] + x_movement, p1.x3y3[1])

                            p1.x2y2 = line_one_top
                            p1.x3y3 = line_one_bottom

                            p2.x1y1 = line_one_top
                            p2.x4y4 =line_one_bottom 

                            line_two_top = (p2.x2y2[0] + x_movement, p2.x2y2[1])
                            line_two_bottom = (p2.x3y3[0] - x_movement, p2.x3y3[1])

                            p2.x2y2 = line_two_top
                            p2.x3y3 = line_two_bottom

                            p3.x1y1 = line_two_top
                            p3.x4y4 = line_two_bottom 
                    else:
                        y_movement = min_height*(movement_proportion/100)

                        if trapezoid_pattern == "A":

                            line_one_top = (p2.x2y2[0], p2.x2y2[1] + y_movement)
                            line_one_bottom = (p2.x1y1[0], p2.x1y1[1] - y_movement)

                            p2.x2y2 = line_one_top
                            p2.x1y1 = line_one_bottom

                            p1.x3y3 = line_one_top
                            p1.x4y4 = line_one_bottom

                            line_two_top = (p2.x3y3[0], p2.x3y3[1] - y_movement)
                            line_two_bottom = (p2.x4y4[0], p2.x4y4[1] + y_movement)

                            p2.x3y3  = line_two_top
                            p2.x4y4  = line_two_bottom

                            p3.x1y1 = line_two_bottom
                            p3.x2y2 = line_two_top
                        else:

                            line_one_top = (p2.x2y2[0], p2.x2y2[1] - y_movement)
                            line_one_bottom = (p2.x1y1[0], p2.x1y1[1] + y_movement)

                            p2.x2y2 = line_one_top
                            p2.x1y1 = line_one_bottom

                            p1.x3y3 = line_one_top
                            p1.x4y4 = line_one_bottom

                            line_two_top = (p2.x3y3[0], p2.x3y3[1] + y_movement)
                            line_two_bottom = (p2.x4y4[0], p2.x4y4[1] - y_movement)

                            p2.x3y3  = line_two_top
                            p2.x4y4  = line_two_bottom

                            p3.x1y1 = line_two_bottom
                            p3.x2y2 = line_two_top

    elif type_choice == "rhombus":

        if page.num_panels > 1:
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

                    for child in [p1, p2, p3]:

                        if child.width < min_width:
                            min_width = child.width
                        
                        if child.height < min_height:
                            min_height = child.height

                    trapezoid_pattern = np.random.choice(["left", "right"])

                    movement_proportion = np.random.randint(10, 50)

                    if panel.orientation == "h":
                        
                        x_movement = min_width*(movement_proportion/100)

                        if trapezoid_pattern == "left":
                            line_one_top = (p1.x2y2[0] - x_movement, p1.x2y2[1])
                            line_one_bottom = (p1.x3y3[0] + x_movement, p1.x3y3[1])

                            p1.x2y2 = line_one_top
                            p1.x3y3 = line_one_bottom

                            p2.x1y1 = line_one_top
                            p2.x4y4 =line_one_bottom 

                            line_two_top = (p2.x2y2[0] - x_movement, p2.x2y2[1])
                            line_two_bottom = (p2.x3y3[0] + x_movement, p2.x3y3[1])

                            p2.x2y2 = line_two_top
                            p2.x3y3 = line_two_bottom

                            p3.x1y1 = line_two_top
                            p3.x4y4 = line_two_bottom 
                        
                        else:

                            line_one_top = (p1.x2y2[0] + x_movement, p1.x2y2[1])
                            line_one_bottom = (p1.x3y3[0] - x_movement, p1.x3y3[1])

                            p1.x2y2 = line_one_top
                            p1.x3y3 = line_one_bottom

                            p2.x1y1 = line_one_top
                            p2.x4y4 =line_one_bottom 

                            line_two_top = (p2.x2y2[0] + x_movement, p2.x2y2[1])
                            line_two_bottom = (p2.x3y3[0] - x_movement, p2.x3y3[1])

                            p2.x2y2 = line_two_top
                            p2.x3y3 = line_two_bottom

                            p3.x1y1 = line_two_top
                            p3.x4y4 = line_two_bottom 
                    else:
                        y_movement = min_height*(movement_proportion/100)

                        if trapezoid_pattern == "right":

                            line_one_top = (p2.x2y2[0], p2.x2y2[1] + y_movement)
                            line_one_bottom = (p2.x1y1[0], p2.x1y1[1] - y_movement)

                            p2.x2y2 = line_one_top
                            p2.x1y1 = line_one_bottom

                            p1.x3y3 = line_one_top
                            p1.x4y4 = line_one_bottom

                            line_two_top = (p2.x3y3[0], p2.x3y3[1] + y_movement)
                            line_two_bottom = (p2.x4y4[0], p2.x4y4[1] - y_movement)

                            p2.x3y3  = line_two_top
                            p2.x4y4  = line_two_bottom

                            p3.x1y1 = line_two_bottom
                            p3.x2y2 = line_two_top
                        else:

                            line_one_top = (p2.x2y2[0], p2.x2y2[1] - y_movement)
                            line_one_bottom = (p2.x1y1[0], p2.x1y1[1] + y_movement)

                            p2.x2y2 = line_one_top
                            p2.x1y1 = line_one_bottom

                            p1.x3y3 = line_one_top
                            p1.x4y4 = line_one_bottom

                            line_two_top = (p2.x3y3[0], p2.x3y3[1] - y_movement)
                            line_two_bottom = (p2.x4y4[0], p2.x4y4[1] + y_movement)

                            p2.x3y3  = line_two_top
                            p2.x4y4  = line_two_bottom

                            p3.x1y1 = line_two_bottom
                            p3.x2y2 = line_two_top

    return page

def box_transform_page(page, type_choice=None):

    type_choice = "fprho" 

    if type_choice == "fprho":
        if len(page.children) > 1:

            for idx in range(0, len(page.children)-1):

                p1 = page.get_child(idx)
                p2 = page.get_child(idx+1)


                change_proportion = np.random.randint(10, 25)
                change_proportion /= 100
                direction = np.random.choice(["rup", "lup"])

                if p1.orientation == "h":

                    change_max = min([(p1.x4y4[1] - p1.x1y1[1]), (p2.x4y4[1] - p2.x1y1[1])])
                    change = change_max*change_proportion
                    line_top = p2.x1y1
                    line_bottom = p2.x2y2

                    if len(p1.children) > 0:
                        move_children_to_line(p1, (line_top, line_bottom), change, "h", direction)
                    else:
                        if direction == "rup":
                            p1.x4y4 = (p1.x4y4[0], p1.x4y4[1] + change)
                        else:
                            p1.x4y4 = (p1.x4y4[0], p1.x4y4[1] - change)

                    if len(p2.children) > 0:
                        move_children_to_line(p2, (line_top, line_bottom), change, "h", direction)
                    else:
                        if direction == "rup":
                            p2.x1y1 = (p2.x1y1[0], p2.x1y1[1] + change)
                        else:
                            p2.x1y1 = (p2.x1y1[0], p2.x1y1[1] - change)
                        # if len(panel.children) > 0:
                else:
                    change_max = min([(p1.x2y2[0] - p1.x1y1[0]), (p2.x2y2[0] - p2.x1y1[0])])
                    change = change_max*change_proportion

                    line_top = p2.x1y1
                    line_bottom = p2.x4y4

                    if len(p1.children) > 0:
                        move_children_to_line(p1, (line_top, line_bottom), change, "v", direction)
                    else:
                        if direction == "rup":
                            p1.x2y2 = (p1.x2y2[0] - change, p1.x2y2[1])
                        else:
                            p1.x2y2 = (p1.x2y2[0] + change, p1.x2y2[1])
                    
                    if len(p2.children) > 0:
                        move_children_to_line(p2, (line_top, line_bottom), change, "v", direction)
                    else:
                        if direction == "rup":
                            p2.x1y1 = (p2.x1y1[0] - change, p2.x1y1[1])
                        else:
                            p2.x1y1 = (p2.x1y1[0] + change, p2.x1y1[1])


            # If panel has children
                # find all children that fall on line to be changed
            # Else just change the panel's coords

    return page
    
def add_transforms(page):
    # Transform types

    # TODO: Add page zig zag
    # TODO: Add boundary removal

    # Allow choosing multiple
    transform_choice = ["slice", "box"]
    # transform_choice = ["slice"]
    # Slicing panels
    # Works best with large panels
    if "slice" in transform_choice:
        page = single_slice_panels(page)

        # Makes v cuts happen more often 1/4 chance
        if np.random.choice([0, 1, 2, 3]) == 1:
            page = single_slice_panels(page)
    
    if "box" in transform_choice:

        # page = box_transform_panels(page)
        page = box_transform_page(page)

    return page 

def shrink_panels(page):

    panels = []
    if len(page.leaf_children) < 1:
        get_leaf_panels(page, panels)
        page.leaf_children = panels
    else:
        panels = page.leaf_children


    for panel in panels:
        pco = pyclipper.PyclipperOffset()
        pco.AddPath(panel.get_polygon(), pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
        solution = pco.Execute(-25.0)

        changed_coords = []
        if len(solution) > 0:
            for item in solution[0]:
                changed_coords.append(tuple(item))

            changed_coords.append(changed_coords[0])

            panel.coords = changed_coords
            panel.x1y1 = changed_coords[0]
            panel.x2y2 = changed_coords[1]
            panel.x3y3 = changed_coords[2]
            panel.x4y4 = changed_coords[3]
        else:
            print(panel.coords)


    return page

def random_remove_panel(page):

    # 1 in 100 chance
    if np.random.random() > 0.99:
        if page.num_panels > 3:
            remove_number = np.random.choice([1, 2])

            for i in range(remove_number):
                page.leaf_children.pop()

    return page

def random_add_background(page, image_dir, image_dir_len, image_dir_path):

    # 1 in 100 chance
    if np.random.random() > 0.99: 
        idx = np.random.randint(0, image_dir_len)
        page.background = image_dir_path + image_dir[idx]

    return page

# Page creators
def create_single_panel_metadata(panel, image_dir, image_dir_len, image_dir_path, font_files, text_dataset, speech_bubble_files, speech_bubble_tags):

    
    # Image inside used
    # Part of image cropped
        # Currently set to use panel part
    select_image_idx = np.random.randint(0, image_dir_len)
    select_image = image_dir[select_image_idx]
    panel.image = image_dir_path+select_image

    num_speech_bubbles = np.random.randint(0,3)
    num_speech_bubbles = 1
    text_dataset_len = len(text_dataset)
    font_dataset_len = len(font_files)
    speech_bubble_dataset_len = len(speech_bubble_files)

    # Associated speech bubbles
    for speech_bubble in range(num_speech_bubbles):



        font_idx = np.random.randint(0, font_dataset_len)
        font = font_files[font_idx]

        speech_bubble_file_idx = np.random.randint(0, speech_bubble_dataset_len)
        speech_bubble_file = speech_bubble_files[speech_bubble_file_idx]
        speech_bubble_writing_area = speech_bubble_tags[speech_bubble_tags['imagename'] == speech_bubble_file]['label']
        speech_bubble_writing_area = json.loads(speech_bubble_writing_area.values[0])

        texts = []
        texts_indices = []
        for i in range(len(speech_bubble_writing_area)):
            text_idx = np.random.randint(0, text_dataset_len)
            texts_indices.append(text_idx)
            text = text_dataset.iloc[text_idx].to_dict()
            texts.append(text)

        # resize bubble to < 40% of panel area
        max_area = panel.area*0.4
        new_area = np.random.random()*(max_area - max_area*0.375)
        new_area = max_area - new_area

        
        # Put location of bubble in panel

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
        # location = tuple(min_coord)
        speech_bubble = SpeechBubble(texts, texts_indices, font, speech_bubble_file, speech_bubble_writing_area, new_area, location)
        panel.speech_bubbles.append(speech_bubble)

def populate_panels(page, image_dir, image_dir_len, image_dir_path, font_files, text_dataset, speech_bubble_files, speech_bubble_tags):

    for child in page.leaf_children:

        create_single_panel_metadata(child,
                                     image_dir,
                                     image_dir_len,
                                     image_dir_path,
                                     font_files,
                                     text_dataset,
                                     speech_bubble_files,
                                     speech_bubble_tags
                                     )
    # TODO: Address bubble overlap
    return page

def get_base_panels(num_panels=0, layout_type=None):

    # TODO: Skew panel number distribution

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
    page = Page(coords, layout_type, num_panels)

    # TODO: Fit in getting black pages sperately

    if layout_type == "v":
        max_num_panels = 4
        if num_panels < 1:
            num_panels = np.random.choice([3, 4])
            page.num_panels = num_panels

        draw_n_shifted(num_panels, page, "v")
        
    elif layout_type == "h":
        max_num_panels = 5
        if num_panels < 1:
            num_panels = np.random.randint(3, max_num_panels+1)
            page.num_panels = num_panels

        draw_n_shifted(num_panels, page, "h")

    elif layout_type == "vh":
        
        max_num_panels = 8
        if num_panels < 1:
            num_panels = np.random.randint(2, max_num_panels+1)
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
            type_choice = np.random.choice(["eq", "uneq", "div", "trip", "twoonethree"]) 

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

            elif type_choice == "twoonethree":

                draw_two_shifted(page, horizontal_vertical)

                choice_idx = choose(page)
                choice = page.get_child(choice_idx)

                next_div = invert_for_next(horizontal_vertical)

                draw_n_shifted(3, choice, next_div)

        if num_panels == 5:

            # Draw two rectangles 
            horizontal_vertical = np.random.choice(["h", "v"])
            
            type_choice = np.random.choice(["eq", "uneq", "div", "twotwothree", "threetwotwo", "fourtwoone"])

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
                draw_two_shifted(choice.get_child(0), next_div, shift=set_shift)
                draw_two_shifted(choice.get_child(1), next_div, shift=set_shift)

            # Draw two rectangles
            elif type_choice == "div":
                draw_two_shifted(page, horizontal_vertical, shift=0.5)
                next_div = invert_for_next(horizontal_vertical)

                # Divide both equally
                draw_two_shifted(page.get_child(0), next_div)
                draw_two_shifted(page.get_child(1), next_div)

                # Pick one of all of them and divide into two
                page_child_chosen = np.random.choice(page.children)
                choice_idx, left_choices = choose_and_return_other(page_child_chosen)
                choice = page_child_chosen.get_child(choice_idx)

                next_div = invert_for_next(next_div)
                draw_two_shifted(choice, horizontal_vertical=next_div, shift=0.5)
        
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
            
            type_choice = np.random.choice(["tripeq", "tripuneq", "twofourtwo","twothreethree", "fourtwotwo"])

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
                        shift_choice = np.random.randint(choice_min, choice_max)
                        choice_max = choice_max + ((100/n) - shift_choice)
                        shifts.append(shift_choice)
                    
                    to_add_or_remove = (100 - sum(shifts))/len(shifts)

                    normalized_shifts = []
                    for shift in shifts:
                        new_shift = shift + to_add_or_remove
                        normalized_shifts.append(new_shift/100)

                    draw_n_shifted(3, panel, next_div, shifts=normalized_shifts) 

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
            
            types = ["twothreefour", "threethreetwotwo", "threefourtwoone","threethreextwoone","fourthreextwo"]
            type_choice = np.random.choice(types)

            # Draw two split 3-4 - HV
            if type_choice == "twothreefour":
                horizontal_vertical = np.random.choice(["h", "v"])

                draw_two_shifted(page, horizontal_vertical, shift=0.5)

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

                draw_n_shifted(3, other, next_div, shifts=normalized_shifts) 

            # Draw 3 split 3-2-2 - H only
            elif type_choice == "threethreetwotwo":
                draw_n(3, page, "h")

                choice_idx, left_choices = choose_and_return_other(page)
                choice = page.get_child(choice_idx)

                draw_n_shifted(3, choice, "v")
                draw_two_shifted(page.get_child(left_choices[0]), "v")
                draw_two_shifted(page.get_child(left_choices[1]), "v")

            # Draw 3 split 4-2-1 - H only
            elif type_choice == "threefourtwoone":
                draw_n(3, page, "h")
                choice_idx, left_choices = choose_and_return_other(page)
                choice = page.get_child(choice_idx)
                other_idx = np.random.choice(left_choices)
                other = page.get_child(other_idx)

                draw_n_shifted(4, choice, "v")
                draw_two_shifted(other, "v")

            # Draw 3 split 3-3-1 - H
            elif type_choice == "threethreextwoone":
                draw_n(3, page, "h")
                choice_idx, left_choices = choose_and_return_other(page)
                choice = page.get_child(choice_idx)
                other = page.get_child(left_choices[0])

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

                draw_n_shifted(3, other, "v", shifts=normalized_shifts)

            # Draw 4 split 3x2 - HV
            elif type_choice == "fourthreextwo":
                horizontal_vertical = np.random.choice(["h", "v"])
                draw_n(4, page, horizontal_vertical)

                choice_idx, left_choices = choose_and_return_other(page)

                next_div = invert_for_next(horizontal_vertical)
                for panel in left_choices:
                    draw_two_shifted(page.get_child(panel), next_div)
            
        if num_panels == 8:
            types = ["fourfourxtwoeq", "fourfourxtwouneq", "threethreethreetwo", "threefourtwotwo", "threethreefourone"]
            type_choice = np.random.choice(types) 

            # Draw 4 x 2
            if type_choice == "fourfourxtwoeq" or type_choice =="fourfourxtwouneq":
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

                for panel in page.children:
                    
                    draw_two_shifted(panel, "v",shift=set_shift)
            
            if type_choice in types[2:]:
                # Draw three - H
                draw_n(3, page, "h")

                # Draw 3 3-3-2 - H
                if type_choice == "threethreethreetwo":
                    choice_idx, left_choices = choose_and_return_other(page)
                    choice = page.get_child(choice_idx)
                    draw_two_shifted(choice, "v")

                    for panel in left_choices:
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

                        draw_n_shifted(3, page.get_child(panel), "v", shifts=normalized_shifts)

                # Draw 3 4-2-2 - H
                elif type_choice == "threefourtwotwo":
                    choice_idx, left_choices = choose_and_return_other(page)
                    choice = page.get_child(choice_idx)

                    draw_n_shifted(4, choice, "v")

                    for panel in left_choices:
                        draw_two_shifted(page.get_child(panel), "v")
                    
                # Draw 3 3-4-1 - H 

                elif type_choice == "threethreefourone":
                    choice_idx, left_choices = choose_and_return_other(page)
                    choice = page.get_child(choice_idx)
                    other_idx = np.random.choice(left_choices)
                    other = page.get_child(other_idx)

                    #3
                    draw_n_shifted(3, choice, "v")

                    #4
                    # Some issue with the function calls and seeding
                    n = 4
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
                    
                    draw_n_shifted(4, other, "v", shifts=normalized_shifts)

    return page 
     
# TODO: Figure out page type distributions
def create_page_metadata(image_dir, image_dir_len, image_dir_path, font_files, text_dataset, speech_bubble_files, speech_bubble_tags):

    # Select page type
    # Select number of panels on the page
        # between 1 and 8
    # Select panel boundary type
    # Select panel boundary widths

    page = get_base_panels(0, None)
    page = add_transforms(page)
    page = shrink_panels(page)
    page = populate_panels(page,
                           image_dir,
                           image_dir_len,
                           image_dir_path,
                           font_files,
                           text_dataset,
                           speech_bubble_files,
                           speech_bubble_tags
                           )

    page = random_remove_panel(page)
    page = random_add_background(page, image_dir, image_dir_len, image_dir_path)

    return page 
