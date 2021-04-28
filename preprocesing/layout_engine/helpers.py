import numpy as np
import math
import random
from PIL import Image, ImageDraw, ImageFont

def crop_image_only_outside(img,tol=0):
    # img is 2D image data
    # tol  is tolerance
    mask = img>tol
    m,n = img.shape
    mask0,mask1 = mask.any(0),mask.any(1)
    col_start,col_end = mask0.argmax(),n-mask0[::-1].argmax()
    row_start,row_end = mask1.argmax(),m-mask1[::-1].argmax()
    return img[row_start:row_end,col_start:col_end]

def invert_for_next(current):
    if current == "h":
        return "v"
    else:
        return "h"

def choose(parent):

    choice_idx = np.random.randint(0, len(parent.children))

    return choice_idx

def choose_and_return_other(parent):

    choices = list(range(0, len(parent.children)))
    choice_idx = np.random.choice(choices)

    choices.remove(choice_idx)

    return choice_idx, choices

def get_min_area_panels(panel, min_area=0.1, ret_panels=[]):

    for child in panel.children:

        if len(child.children) > 1:
            get_min_area_panels(child, min_area, ret_panels)
        else:
            if child.area_proportion >= min_area and not child.sliced:
                ret_panels.append(child)

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

def get_leaf_panels(page, panels=[]):

    for child in page.children:
        
        if len(child.children) > 0:
            get_leaf_panels(child, panels)
        else:
            panels.append(child)

def find_parent_with_multiple_children(page, n):

    panels =[]    
    if len(page.leaf_children) < 1:
        get_leaf_panels(page, panels)
        page.leaf_children = panels
    else:
        panels = page.leaf_children

    relevant_panels = []

    for panel in panels:
        if panel.parent not in relevant_panels:
            if len(panel.parent.children) == n:
                relevant_panels.append(panel.parent)
    
    return relevant_panels

def move_child_to_line(point, change, old_line, orientation):

    if orientation == "h":
        old_line_length = old_line[1][0] - old_line[0][0]

        movement = (change*(point[0] - old_line[1][0]))/old_line_length

        return movement
    else:

        old_line_length = (old_line[1][1] - old_line[0][1])

        r1 = change/old_line_length

        movement = (change*(point[1] - old_line[1][1]))/old_line_length

        return movement

def move_children_to_line(parent, line, change, orientation, direction):

    x_value = line[0][0]
    y_value = line[0][1]
    if orientation == "h":

        if direction == "rup":
            for child in parent.children:
                if len(child.children) > 0:
                    move_children_to_line(child, line, change, orientation, direction)
                else:
                    for idx, coord in enumerate(child.coords):
                        if coord[1] == y_value:
                            mvmnt = move_child_to_line(coord, change, line, orientation)
                            child.coords[idx] = (coord[0], coord[1] - mvmnt)
                            child.non_rect = True
        else:
            for child in parent.children:
                if len(child.children) > 0:
                    move_children_to_line(child, line, change, orientation, direction)
                else:
                    for idx, coord in enumerate(child.coords):
                        if coord[1] == y_value:
                            mvmnt = move_child_to_line(coord, change, line, orientation)
                            child.coords[idx] = (coord[0], coord[1] + mvmnt)
                            child.non_rect = True

    else:
        if direction == "rup":
            for child in parent.children:
                if len(child.children) > 0:
                    move_children_to_line(child, line, change, orientation, direction)
                else:
                    for idx, coord in enumerate(child.coords):
                        if coord[0] == x_value:
                            mvmnt = move_child_to_line(coord, change, line, orientation)
                            child.coords[idx] = (coord[0] + mvmnt, coord[1])
                            child.non_rect = True
        else:
            for child in parent.children:
                if len(child.children) > 0:
                    move_children_to_line(child, line, change, orientation, direction)
                else:
                    for idx, coord in enumerate(child.coords):
                        if coord[0] == x_value:
                            mvmnt = move_child_to_line(coord, change, line, orientation)
                            child.coords[idx] = (coord[0] - mvmnt, coord[1])
                            child.non_rect = True