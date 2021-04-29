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