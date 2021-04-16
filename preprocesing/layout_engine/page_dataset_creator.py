import numpy as np 
import math
import time
from copy import deepcopy
import random

# TODO: Figure out page type distributions

class Panel:

    def __init__(self, dims, name, parent, children=[]):

        self.x1y1 = dims[0]
        self.x2y2 = dims[1]
        self.x3y3 = dims[2]
        self.x4y4 = dims[3]
        self.name = name
        self.parent = parent

        self.lines = [
            (self.x1y1, self.x2y2),
            (self.x2y2, self.x3y3),
            (self.x3y3, self.x4y4),
            (self.x4y4, self.x1y1)
        ]

        self.area = (self.x2y2[0] - self.x1y1[0])*(self.x3y3[1] - self.x2y2[1])
        self.area_proportion = round(self.area/(2400*1700), 2)

        adjacency_list = dict(
            above = [],
            below = [],
            left = [],
            right = []
        )

        self.children = children
    
    def get_relative_location(self, panel):
        
        pos = ""
        # Is left of
        if self.x1y1[0] < panel.x1y1[0]:
            pos = "left"
        # Same x-axis
        elif self.x1y1[0] == panel.x1y1[0]:
            # Is below of
            if self.x1y1[1] < panel.x1y1[1]:
                pos = "below" 
            # Same y-axis
            elif self.x1y1[1] == panel.x1y1[1]:
                pos = "on"
            # Is above of
            else:
                pos = "above"
        # Is right of
        else:
            pos = "right"
        
        return pos
    
    def get_polygon(self):

        return (
            self.x1y1,
            self.x2y2,
            self.x3y3,
            self.x4y4,
            self.x1y1
        )

    def is_adjacent(self, panel):

        for l1 in self.lines:
            for l2 in panel.lines:
                if l1 == l2:
                    return True
        return False
    
    def add_child(self, panel):

        self.children.append(panel)
    
    def add_children(self, panels):

        for panel in panels:
            self.add_child(panel)
    
    def get_child(self, idx):

        return self.children[idx]

class Page(Panel):

    def __init__(self, dims, page_type, num_panels, children=[]):
        super().__init__(dims, "page", None, [])

        self.num_panels = num_panels
        self.page_type = page_type

def draw_n_shifted(n, parent, horizontal_vertical, shifts=[]):

        topleft = parent.x1y1
        topright = parent.x2y2
        bottomright = parent.x3y3
        bottomleft = parent.x4y4

        # Allow each inital panel to grow to up to 75% of 100/n
        choice_max = round((100/n)*1.5)
        choice_min = round((100/n)*0.5)
        if len(shifts) < 1:
            for i in range(0, n):
                shift_choice = np.random.randint(choice_min, choice_max)
                choice_max = choice_max + ((100/n) - shift_choice)
                shifts.append(shift_choice)
        
            to_add_or_remove = (100 - sum(shifts))/len(shifts)

            normalized_shifts = []
            for shift in shifts:
                new_shift = shift + to_add_or_remove
                normalized_shifts.append(new_shift/100)
        else:
            normalized_shifts = shifts


        if horizontal_vertical == "h":
            shift_level = 0.0 
            for i in range(0, n):
                if i == 0:
                    x1y1 = topleft
                    x2y2 = topright
                else:
                   shift_level += normalized_shifts[i-1]
                   x1y1 = (bottomleft[0], topleft[1] + (bottomleft[1] - topleft[1])*shift_level)
                   x2y2 = (bottomright[0], topright[1] + (bottomright[1]- topright[1])*shift_level)
                
                if i == (n-1):
                    x3y3 = bottomright
                    x4y4 = bottomleft
                else:
                    next_shift_level = shift_level + normalized_shifts[i]
                    x3y3 = (bottomright[0], topright[1] + (bottomright[1]- topright[1])*next_shift_level)
                    x4y4 = (bottomleft[0], topleft[1] + (bottomleft[1] - topleft[1])*next_shift_level)

                poly_dims = (x1y1, x2y2, x3y3, x4y4)
                poly = Panel(poly_dims, parent.name+"-"+str(i), parent=parent, children=[])
                parent.add_child(poly)
        
        if horizontal_vertical == "v":
            shift_level = 0.0 
            for i in range(0, n):
                if i == 0:
                    x1y1 = topleft
                    x4y4 = bottomleft 
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

                poly_dims = (x1y1, x2y2, x3y3, x4y4)
                poly = Panel(poly_dims, parent.name+"-"+str(i), parent=parent, children=[])
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

                poly_dims = (x1y1, x2y2, x3y3, x4y4)
                poly = Panel(poly_dims, parent.name+"-"+str(i), parent=parent, children=[])
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

                poly_dims = (x1y1, x2y2, x3y3, x4y4)
                poly = Panel(poly_dims, parent.name+"-"+str(i), parent=parent, children=[])
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

        poly1_dims = (r1x1y1, r1x2y2, r1x3y3, r1x4y4)

        r2x1y1 = (bottomleft[0], topleft[1] + (bottomleft[1] - topleft[1])*shift)
        r2x2y2 = (bottomright[0], topright[1] + (bottomright[1] - topright[1])*shift)
        r2x3y3 = bottomright
        r2x4y4 = bottomleft

        poly2_dims = (r2x1y1, r2x2y2, r2x3y3, r2x4y4, r2x1y1)

        poly1 = Panel(poly1_dims, parent.name + "-0", parent=parent, children=[])
        poly2 = Panel(poly2_dims, parent.name + "-1", parent=parent, children=[])

        parent.add_children([poly1, poly2])
    
    if horizontal_vertical == "v":
        
        r1x1y1 = topleft
        r1x2y2 = (topleft[0] + (topright[0] - topleft[0])*shift, topright[1])
        r1x3y3 = (bottomleft[0] + (bottomright[0] - bottomleft[0])*shift, bottomright[1])
        r1x4y4 = bottomleft

        poly1_dims = (r1x1y1, r1x2y2, r1x3y3, r1x4y4, r1x1y1)

        r2x1y1 = (topleft[0] + (topright[0] - topleft[0])*shift, topright[1])
        r2x2y2 = topright
        r2x3y3 = bottomright
        r2x4y4 = (bottomleft[0] + (bottomright[0] - bottomleft[0])*shift, bottomright[1])

        poly2_dims = (r2x1y1, r2x2y2, r2x3y3, r2x4y4, r2x1y1)

        poly1 = Panel(poly1_dims, parent.name + "-0", parent, children=[])
        poly2 = Panel(poly2_dims, parent.name + "-1", parent, children=[])

        parent.add_children([poly1, poly2])

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
            if child.area_proportion >= min_area:
                ret_panels.append(child)

def single_slice_panels(page):

    # Remove panels which are too small 
    relevant_panels = [] 
    get_min_area_panels(page, 0.1, ret_panels=relevant_panels) 

    # Shuffle panels for randomness
    random.shuffle(relevant_panels)

    # single slice close
    type_choice =  np.random.choice(["center", "side"])
    type_choice =  "center"

    # TODO: Remember to add number of panels increase to page 
    # Center
    if type_choice == "center":
        if len(relevant_panels) > 1:
            number_to_slice = np.random.randint(1, len(relevant_panels))
        else:
            number_to_slice = 1

        for idx in range(0, number_to_slice):
            panel = relevant_panels[idx]

            # Decide which direction to cut in
            horizontal_vertical = np.random.choice(["h", "v"])

            # Get center line
            # Vertical slice
            if horizontal_vertical == "v":
                panel_chosen_dim_length = (panel.x2y2[0] - panel.x1y1[0])/2

                # Slice panel
                draw_n(2, panel, "v")

                # Skew it left or right
                skew_side = np.random.choice(["left", "right"])

                # Skew it by a percentage
                skew_amount = np.random.randint(20, 100)/100
                skew_amount = skew_amount*panel_chosen_dim_length

                # Perform transform
                p1 = panel.get_child(0)
                p2 = panel.get_child(1)
                if skew_side == "left":
                    p1.x2y2 = (p1.x2y2[0] - skew_amount, p1.x2y2[1])
                    p1.x3y3 = (p1.x3y3[0] + skew_amount, p1.x3y3[1])

                    p2.x1y1 = (p2.x1y1[0] - skew_amount, p2.x1y1[1])
                    p2.x4y4 = (p2.x4y4[0] + skew_amount, p2.x4y4[1])
                else:
                    p1.x2y2 = (p1.x2y2[0] + skew_amount, p1.x2y2[1])
                    p1.x3y3 = (p1.x3y3[0] - skew_amount, p1.x3y3[1])

                    p2.x1y1 = (p2.x1y1[0] + skew_amount, p2.x1y1[1])
                    p2.x4y4 = (p2.x4y4[0] - skew_amount, p2.x4y4[1])
            # Horizontal slice
            else:
                panel_chosen_dim_length = (panel.x3y3[1] - panel.x2y2[1])/2

                # Slice panel
                draw_n(2, panel, "h")

                # Skew it left or right
                skew_side = np.random.choice(["down", "up"])

                # Skew it by a percentage
                skew_amount = np.random.randint(20, 100)/100
                skew_amount = skew_amount*panel_chosen_dim_length

                p1 = panel.get_child(0)
                p2 = panel.get_child(1)
                if skew_side == "down":
                    p1.x4y4 = (p1.x4y4[0], p1.x4y4[1] + skew_amount)
                    p1.x3y3 = (p1.x3y3[0], p1.x3y3[1] - skew_amount)

                    p2.x1y1 = (p2.x1y1[0], p2.x1y1[1] + skew_amount)
                    p2.x2y2 = (p2.x2y2[0], p2.x2y2[1] - skew_amount)

                else:
                    p1.x4y4 = (p1.x4y4[0], p1.x4y4[1] - skew_amount)
                    p1.x3y3 = (p1.x3y3[0], p1.x3y3[1] + skew_amount)

                    p2.x1y1 = (p2.x1y1[0], p2.x1y1[1] - skew_amount)
                    p2.x2y2 = (p2.x2y2[0], p2.x2y2[1] + skew_amount)

    # Sides

    return page

def add_transforms(page):
    # Transform types

    # Allow choosing multiple
    transform_choice = np.random.choice(["slice", "bend", "boundary"])
    transform_choice = "slice"

    # Slicing panels
    if transform_choice == "slice":
        page = single_slice_panels(page)


        # double slice 
            # V
            # sides

    # 4 panel skew
    # 3 panel skew
    # 2 panel skew
        # 1 panel moves and two smaller ones besides it get skewed

    # Box transforms
        # Turn into trapezoid
            # All rows
        # Turn into rhombus
            # only 3 panels or greater types
        # Full page back and forth

    # Boundary removal 
        # bottom panel
            # Single side
            # all sides
        # top panel
            # Single side
            # all sides

    return page 

def add_misalignment(panels):

    # Mis align types - apply to full or half page
        # Top to bottom left right left right
        # Left to right up down
        # bottom left to top right shrink
            # With above two types
        # Sin wave across screen

        # Center and wavy
        # Just panel movement

    return panels

def shrink_panels(panels):

    return panels

def create_single_panel_metadata():
    # Coords
    # Dims
    pass


def get_base_panels(num_panels=0, layout_type=None):

    # TODO: Skew panel number distribution

    topleft = (0.0, 0.0)
    topright = (1700, 0.0)
    bottomleft = (0.0, 2400)
    bottomright = (1700, 2400)
    dims = [
        topleft,
        topright,
        bottomright,
        bottomleft
    ]

    if layout_type is None:
        layout_type = np.random.choice(["v", "h", "vh"])

    # Panels encapsulated and returned within page
    page = Page(dims, layout_type, num_panels)

    # TODO: Fit in getting black pages sperately

    if layout_type == "v":
        max_num_panels = 4
        if num_panels < 1:
            num_panels = np.random.choice([3, 4])

        draw_n_shifted(num_panels, page, "v")
        
    elif layout_type == "h":
        max_num_panels = 5
        if num_panels < 1:
            num_panels = np.random.randint(3, max_num_panels+1)
        draw_n_shifted(num_panels, page, "h")

    
    elif layout_type == "vh":
        
        max_num_panels = 8
        if num_panels < 1:
            num_panels = np.random.randint(2, max_num_panels+1)

        if num_panels == 2:
            # Draw 2 rectangles
                # vertically or horizontally
            horizontal_vertical = np.random.choice(["h", "v"])
            draw_two_shifted(page, horizontal_vertical)

        if num_panels == 3:
            # Draw 2 rectangles
                # Vertically or Horizontally

            horizontal_vertical = np.random.choice(["h", "v"])
            horizontal_vertical = "v"
            draw_two_shifted(page, horizontal_vertical)

            next_div = invert_for_next(horizontal_vertical)

            # Pick one and divide it into 2 rectangles
            choice_idx = choose(page)
            choice = page.get_child(choice_idx)

            draw_two_shifted(choice, next_div)

        if num_panels == 4:
            horizontal_vertical = np.random.choice(["h", "v"])
            type_choice = np.random.choice(["eq", "uneq", "div", "trip"]) 

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
                # panels = draw_n_shifted(4, *dims, "h")
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
     
def create_page_metadata():

    # Select page type
    # Select number of panels on the page
        # between 1 and 8
    # Select panel boundary type
    # Select panel boundary widths
    # TODO: Remember some panels can just be left blank

    page = get_base_panels(5, "vh")
    transformed_page = add_transforms(page)

    return transformed_page
