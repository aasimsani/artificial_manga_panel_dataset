import numpy as np
import math
import random
from PIL import Image, ImageDraw, ImageFont

def crop_image_only_outside(img,tol=0):
    """
    Crop the outside of the image where
    the pixels are black

    :param img: image to be cropped

    :type img: PIL.Image

    :param tol: tollerance level, defaults to 0

    :type tol: int, optional

    :return: Cropped image

    :rtype: PIL.Image
    """    
    # img is 2D image data
    # tol  is tolerance
    mask = img>tol
    m,n = img.shape

    mask0,mask1 = mask.any(0),mask.any(1)

    col_start,col_end = mask0.argmax(),n-mask0[::-1].argmax()
    row_start,row_end = mask1.argmax(),m-mask1[::-1].argmax()

    return img[row_start:row_end,col_start:col_end]

def invert_for_next(current):
    """

    A helper function used to invert
    the orientation indicator of the
    next panel based on the current panel 
    i.e. if a parent is horizontal a
    child panel must be vertical

    :param current: Current parent
    orientation

    :type current: str

    :return: child panel orientation

    :rtype: str
    """    
    if current == "h":
        return "v"
    else:
        return "h"

def choose(parent):
    """
    Choose one panel from a parent
    panel's children

    :param parent: Parent panel whose children are
    chosen from

    :type parent: Panel

    :return: Index of chosen child panel

    :rtype: int
    """    

    choice_idx = np.random.randint(0, len(parent.children))

    return choice_idx

def choose_and_return_other(parent):
    """
    Choose a particular panel to return
    randomly and also return panels
    not chosen

    :param parent: parent panel whose
    children are picked from

    :type parent: Panel
    
    :return: A tuple of a chosen child panel index
    and a list the indices of those that weren't

    :rtype: tuple
    """    

    choices = list(range(0, len(parent.children)))
    choice_idx = np.random.choice(choices)

    choices.remove(choice_idx)

    return choice_idx, choices

def get_min_area_panels(panel, min_area=0.1, ret_panels=[]):
    """
    Recursively get a set of panels which have a 
    particular minimum area

    :param panel: parent panel

    :type panel: Panel

    :param min_area: Minimum area as a ratio
    of the page's area, defaults to 0.1

    :type min_area: float, optional

    :param ret_panels: Panels to return, defaults to []

    :type ret_panels: list, optional
    """    

    for child in panel.children:

        if len(child.children) > 1:
            get_min_area_panels(child, min_area, ret_panels)
        else:
            if child.area_proportion >= min_area and not child.sliced:
                ret_panels.append(child)

def get_leaf_panels(page, panels):
    """
    Get panels which are to actually
    be rendered recursively i.e. they 
    are the leaves of the Page-Panel 
    tree

    :param page: Page to be searched

    :type page: Page

    :param panels: A list of panels to be 
    returned by refernce

    :type panels: list
    """    

    # For each child 
    for child in page.children:

        # See if panel has no children 
        # Therefore is a leaf
        if len(child.children) > 0:
            # If has children keep going
            get_leaf_panels(child, panels)
        else:
            # Otherwise put in list to return
            panels.append(child)

def find_parent_with_multiple_children(page, n):
    """
    This function finds parent panels which have
    a particular number of children

    :param page: Page to be searched
    :type page: Page

    :param n: number of children

    :type n: int

    :return: The children of the page
    which hae n children

    :rtype: list

    """    

    panels =[]    

    # Get the leaf panels of a page
    if len(page.leaf_children) < 1:
        get_leaf_panels(page, panels)

        # Store this for future use
        page.leaf_children = panels
    else:
        panels = page.leaf_children

    relevant_panels = []
    
    # Find panels with n children
    for panel in panels:
        if panel.parent not in relevant_panels:
            if len(panel.parent.children) == n:
                relevant_panels.append(panel.parent)
    
    return relevant_panels

def move_child_to_line(point, change, old_line, orientation):
    """
    A helper function that uses the triangle similarity
    theorem which specifies that if one triangle 
    is just a sub triangle of another i.e. is just
    one line drawn from any two sides it's sides
    share a ratio.

    :param point: coordinate to be moved

    :type point: tuple

    :param change: amount the original line was moved 
    as a length

    :type change: float

    :param old_line: original line which was moved

    :type old_line: tuple

    :param orientation: orientation of panel whose
    line was moved therefore the line

    :type orientation: str

    :return: Amount the point needs to be adjusted

    :rtype: float
    """    

    # If the line was moved vertically
    if orientation == "h":

        old_line_length = old_line[1][0] - old_line[0][0]

        # change times the old point's x coordinate minus
        # the old line's second point's x coordinate
        # by the line's length

        # In essence ratio of change/oldline times the difference
        # between the point on the line's x coord i.e the length of
        # the side of the inner triangle times the changed line's length
        movement = (change*(point[0] - old_line[1][0]))/old_line_length

        return movement
    
    # Same as above but if the lien was moved horizontally
    else:

        old_line_length = (old_line[1][1] - old_line[0][1])

        movement = (change*(point[1] - old_line[1][1]))/old_line_length

        return movement

def move_children_to_line(parent, line, change, orientation, direction):
    """
    A helper function that recursively moves the children of a parent
    panel to a particular line which is where the parent panel's
    new side lines using a basic trignometric formula of similar
    triangles

    :param parent: Parent panel which is being transformed

    :type parent: Panel 

    :param line: A set of xy coordinates to move the 
    child panels to

    :type line: tuple

    :param change: How much the parent panel's line moved

    :type change: float

    :param orientation: orientation of the parent panel
    i.e. horizontal or vertical

    :type orientation: str

    :param direction: which of the line's sides went up

    :type direction: str
    """    

    # Points which signify the old line's x and y coords
    x_value = line[0][0]
    y_value = line[0][1]

    # If horizontal
    if orientation == "h":
        # If the right side of the line went up
        if direction == "rup":
            for child in parent.children:
                # If not leaf keep going
                if len(child.children) > 0:
                    move_children_to_line(child, line, change, orientation, direction)

                else:
                    # Move each coordinate to the new line
                    for idx, coord in enumerate(child.coords):
                        # Since we are horizontal the movement is on the y axis
                        # Therefore if any children lie on the old line's y coord
                        # They need to be moved to the new coord
                        if coord[1] == y_value:
                            mvmnt = move_child_to_line(coord, change, line, orientation)
                            child.coords[idx] = (coord[0], coord[1] - mvmnt)
                            child.non_rect = True

        # If the left side of the line went up
        else:
            for child in parent.children:
                # If not leaf keep going
                if len(child.children) > 0:
                    move_children_to_line(child, line, change, orientation, direction)
                else:
                    for idx, coord in enumerate(child.coords):
                        # Since we are horizontal the movement is on the y axis
                        # Therefore if any children lie on the old line's y coord
                        # They need to be moved to the new coord
                        if coord[1] == y_value:
                            mvmnt = move_child_to_line(coord, change, line, orientation)
                            child.coords[idx] = (coord[0], coord[1] + mvmnt)
                            child.non_rect = True
    # If vertical
    else:
        # If the top side of the line went up
        if direction == "rup":
            for child in parent.children:
                # If not leaf keep going
                if len(child.children) > 0:
                    move_children_to_line(child, line, change, orientation, direction)
                else:
                    for idx, coord in enumerate(child.coords):
                        # Since we are vertical the movement is on the x axis
                        # Therefore if any children lie on the old line's x coord
                        # They need to be moved to the new coord
                        if coord[0] == x_value:
                            mvmnt = move_child_to_line(coord, change, line, orientation)
                            child.coords[idx] = (coord[0] + mvmnt, coord[1])
                            child.non_rect = True
        # If the bottom side of the line went up
        else:
            for child in parent.children:
                # If not leaf keep going
                if len(child.children) > 0:
                    move_children_to_line(child, line, change, orientation, direction)
                else:
                    for idx, coord in enumerate(child.coords):
                        # Since we are vertical the movement is on the x axis
                        # Therefore if any children lie on the old line's x coord
                        # They need to be moved to the new coord
                        if coord[0] == x_value:
                            mvmnt = move_child_to_line(coord, change, line, orientation)
                            child.coords[idx] = (coord[0] - mvmnt, coord[1])
                            child.non_rect = True
