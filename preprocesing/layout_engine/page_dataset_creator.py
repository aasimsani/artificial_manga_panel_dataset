from PIL import Image, ImageDraw
import numpy as np 
import math
import time
from copy import deepcopy

# TODO: Figure out page type distributions

def create_single_panel_metadata():

    # Coords
    # Dims
    # 
    pass

def test_render(dims):

    W = 1700
    H = 2400
    print(dims)
    page = Image.new(size=(W,H), mode="L", color="white")
    draw_rect = ImageDraw.Draw(page)

    for rect in dims:
        # draw_rect.rectangle(rect, fill=None, outline="white", width=20)
        draw_rect.line(rect, fill="black", width=20)
        # draw_rect.polygon(rect, fill="red", outline="yellow")

    page.show()

def draw_two(topleft, topright, bottomright, bottomleft, horizontal_vertical):


    if horizontal_vertical == "h":
        r1x1y1 = topleft
        r1x2y2 = topright
        r1x3y3 = (bottomright[0], bottomright[1]/2)
        r1x4y4 = (bottomleft[0], bottomleft[1]/2)

        poly1 = (r1x1y1, r1x2y2, r1x3y3, r1x4y4)

        r2x1y1 = (bottomleft[0], bottomleft[1]/2)
        r2x2y2 = (bottomright[0], bottomright[1]/2)
        r2x3y3 = bottomright
        r2x4y4 = bottomleft

        poly2 = (r2x1y1, r2x2y2, r2x3y3, r2x4y4)
    
    if horizontal_vertical == "v":
        r1x1y1 = topleft
        r1x2y2 = (topright[0]/2, topright[1])
        r1x3y3 = (bottomright[0]/2, bottomright[1])
        r1x4y4 = bottomleft

        poly1 = (r1x1y1, r1x2y2, r1x3y3, r1x4y4)

        r2x1y1 = (topright[0]/2, topright[1])
        r2x2y2 = topright
        r2x3y3 = bottomright
        r2x4y4 = (bottomright[0]/2, bottomright[1])

        poly2 = (r2x1y1, r2x2y2, r2x3y3, r2x4y4)
   
    return poly1, poly2

def draw_three(topleft, topright, bottomright, bottomleft, horizontal_vertical):

    if horizontal_vertical == "h":
        r1x1y1 = topleft
        r1x2y2 = topright
        r1x3y3 = (bottomright[0], bottomright[1]/3)
        r1x4y4 = (bottomleft[0], bottomleft[1]/3)

        poly1 = (r1x1y1, r1x2y2, r1x3y3, r1x4y4)

        r2x1y1 = (bottomleft[0], bottomleft[1]/3)
        r2x2y2 = (bottomright[0], bottomright[1]/3)
        r2x3y3 = (bottomright[0], bottomright[1]*(2/3))
        r2x4y4 = (bottomleft[0], bottomleft[1]*(2/3))

        poly2 = (r2x1y1, r2x2y2, r2x3y3, r2x4y4)

        r3x1y1 = (bottomleft[0], bottomleft[1]*(2/3))
        r3x2y2 = (bottomright[0], bottomright[1]*(2/3))
        r3x3y3 = bottomright
        r3x4y4 = bottomleft 

        poly3 = (r3x1y1, r3x2y2, r3x3y3, r3x4y4)

    
    if horizontal_vertical == "v":
        r1x1y1 = topleft
        r1x2y2 = (topright[0]/3, topright[1])
        r1x3y3 = (bottomright[0]/3, bottomright[1])
        r1x4y4 = bottomleft

        poly1 = (r1x1y1, r1x2y2, r1x3y3, r1x4y4)

        r2x1y1 = (topright[0]/3, topright[1])
        r2x2y2 = (topright[0]*(2/3), topright[1])
        r2x3y3 = (bottomright[0]*(2/3), bottomright[1])
        r2x4y4 = (bottomright[0]/3, bottomright[1])

        poly2 = (r2x1y1, r2x2y2, r2x3y3, r2x4y4)

        r3x1y1 = (topright[0]*(2/3), topright[1])
        r3x2y2 = topright
        r3x3y3 = bottomright
        r3x4y4 = (bottomright[0]*(2/3), bottomright[1])

        poly3 = (r3x1y1, r3x2y2, r3x3y3, r3x4y4)
    
    return poly1, poly2, poly3

def draw_two_shifted(topleft, topright, bottomright, bottomleft, horizontal_vertical, shift=None):

    if shift is None:
        shift_min = 25
        shift_max = 75
        shift = np.random.randint(shift_min, shift_max)
        shift = shift/100

    if horizontal_vertical == "h":
        r1x1y1 = topleft
        r1x2y2 = topright
        r1x3y3 = (bottomright[0], bottomright[1]*shift)
        r1x4y4 = (bottomleft[0], bottomleft[1]*shift)

        poly1 = (r1x1y1, r1x2y2, r1x3y3, r1x4y4)

        r2x1y1 = (bottomleft[0], bottomleft[1]*shift)
        r2x2y2 = (bottomright[0], bottomright[1]*shift)
        r2x3y3 = bottomright
        r2x4y4 = bottomleft

        poly2 = (r2x1y1, r2x2y2, r2x3y3, r2x4y4)
    
    if horizontal_vertical == "v":

        r1x1y1 = topleft
        r1x2y2 = (topright[0]*shift, topright[1])
        r1x3y3 = (bottomright[0]*shift, bottomright[1])
        r1x4y4 = bottomleft

        poly1 = (r1x1y1, r1x2y2, r1x3y3, r1x4y4)

        r2x1y1 = (topright[0]*shift, topright[1])
        r2x2y2 = topright
        r2x3y3 = bottomright
        r2x4y4 = (bottomright[0]*shift, bottomright[1])

        poly2 = (r2x1y1, r2x2y2, r2x3y3, r2x4y4)
   
    return poly1, poly2

def invert_for_next(current):
    if current == "h":
        return "v"
    else:
        return "h"

def create_page_metadata():

    # Select page type
    # Select number of panels on the page
        # between 1 and 8
    # Select panel boundary type
    # Select panel boundary widths

    # Each page is a 2x4 grid

    panel_dims = []

    layout_type = "vh"

    # TODO: Rehaul this to be more standardized
    if layout_type == "v":
        max_num_panels = 4

        # Doesn't guarantee this number due to edge cases and fitting
        num_panels = np.random.randint(1, max_num_panels+1)

        panel_widths = {}
        # Randomly increase or decrease each panel by "x%"
        panel_width_default = 425
        if num_panels > 1:
            for panel in range(0, num_panels-1):

                change = np.random.randint(-50,50)
                pw = round(panel_width_default*(1 - (change/100)), -1)
                panel_widths[panel] = pw 

        # Deal with exceeding width
        total_widths = sum(panel_widths.values())
        if total_widths > 1700:
            extra_width = total_widths - 1700
            to_remove = math.ceil(extra_width/len(panel_widths))
            # divide it amongst the panels
            for panel in panel_widths:
                panel_widths[panel] = (panel_widths[panel] - to_remove)

        last_pw = 1700 - total_widths 
        if last_pw> 0:
            panel_widths[len(panel_widths)] = last_pw 

        panel_coords = []
        current_axis_location = 0        
        for panel in panel_widths:
            x1 = current_axis_location
            y1 = 0.0

            x2 = current_axis_location + panel_widths[panel]
            y2 = 2400

            current_axis_location = x2

            coord = ((x1, y1), (x2, y2))
            panel_coords.append(coord)
        
    # TODO: Rehaul this to be more standardized
    elif layout_type == "h":
        max_num_panels = 6

        num_panels = np.random.randint(1, max_num_panels+1)

        panel_heights = {}
        # Randomly increase or decrease each panel by "x%"
        panel_height_default = 600
        if num_panels > 1:
            for panel in range(0, num_panels-1):

                change = np.random.randint(-25,25)
                ph = round(panel_height_default*(1 - (change/100)), -1)
                panel_heights[panel] = ph 

        # Deal with exceeding height
        total_heights = sum(panel_heights.values())
        if total_heights > 2400:
            extra_height = total_heights - 2400
            to_remove = math.ceil(extra_height/len(panel_heights))
            # divide it amongst the panels
            for panel in panel_heights:
                panel_heights[panel] = (panel_heights[panel] - to_remove)

        last_ph = 2400 - total_heights
        if last_ph> 0:
            panel_heights[len(panel_heights)] = last_ph

        panel_coords = []
        current_axis_location = 0.0 
        for panel in panel_heights:
            x1 = 0.0 
            y1 = current_axis_location

            x2 = 1700
            y2 = current_axis_location + panel_heights[panel]

            current_axis_location = y2

            coord = ((x1, y1), (x2, y2))
            panel_coords.ppend(coord)
    
    elif layout_type == "vh":
        
        max_num_panels = 8
        # num_panels = np.random.randint(2, max_num_panels+1)
        num_panels = 4

        topleft = (0.0, 0.0)
        topright = (1700, 0.0)
        bottomleft = (0.0, 2400)
        bottomright = (1700, 2400)

        if num_panels == 2:
            # Draw 2 rectangles
                # vertically or horizontally
            horizontal_vertical = np.random.choice(["h", "v"])
            p1, p2 = draw_two_shifted(topleft, topright, bottomright, bottomleft, horizontal_vertical)
            ret_list = [p1, p2]
            test_render(ret_list)
    
        if num_panels == 3:
            # Draw 2 rectangles
                # Vertically or Horizontally
                # Pick one and divide it into 2 rectangles

            horizontal_vertical = np.random.choice(["h", "v"])
            p1, p2 = draw_two_shifted(topleft, topright, bottomright, bottomleft, horizontal_vertical)

            next_div = invert_for_next(horizontal_vertical)

            ret_list = []
            pick_one = np.random.random()
            if pick_one > 0.5:
                choice = p1
                p3, p4 = draw_two_shifted(choice[0], choice[1], choice[2], choice[3], next_div)
                ret_list = [p2, p3, p4]
            else:
                choice = p2
                p3, p4 = draw_two_shifted(choice[0], choice[1], choice[2], choice[3], next_div)
                ret_list = [p1, p3, p4]

            test_render(ret_list)

        if num_panels == 4:

            num_base = np.random.choice([2,3])
            num_base = 3
            ret_list = []
            if num_base == 2:
                # Draw two rectangles 
                horizontal_vertical = np.random.choice(["h", "v"])
                p1, p2 = draw_two(topleft, topright, bottomright, bottomleft, horizontal_vertical)

                next_div = invert_for_next(horizontal_vertical)

                type_choice = np.random.choice(["eq", "uneq", "div"]) 
                if type_choice == "eq":
                # Divide each into 2 rectangles equally
                    shift_min = 25
                    shift_max = 75
                    shift = np.random.randint(shift_min, shift_max)
                    shift = shift/100 

                    p3, p4 = draw_two_shifted(p1[0], p1[1], p1[2], p1[3], next_div, shift)
                    p5, p6 = draw_two_shifted(p2[0], p2[1], p2[2], p2[3], next_div, shift)
                    ret_list = [p3, p4, p5, p6]

                # Divide each into 2 rectangles unequally
                elif type_choice == "uneq":
                    p3, p4 = draw_two_shifted(p1[0], p1[1], p1[2], p1[3], next_div)
                    p5, p6 = draw_two_shifted(p2[0], p2[1], p2[2], p2[3], next_div)
                    ret_list = [p3, p4, p5, p6]

                # Pick one and divide into 2 rectangles
                        # Pick one of these two and divide that into 2 rectangles
                elif type_choice == "div":
                    pick_one = np.random.random()
                    if pick_one > 0.5:
                        choice = p1
                        p3, p4 = draw_two_shifted(choice[0], choice[1], choice[2], choice[3], next_div)
                        pick_one_again = np.random.random()
                        next_div = invert_for_next(next_div)
                        if pick_one_again > 0.5:
                            choice = p3
                            p5, p6 = draw_two_shifted(choice[0], choice[1], choice[2], choice[3], next_div)
                            ret_list = [p2, p4, p5, p6]
                        else:
                            choice = p4
                            p5, p6 = draw_two_shifted(choice[0], choice[1], choice[2], choice[3], next_div)
                            ret_list = [p2, p3, p5, p6]
                    else:
                        choice = p2
                        p3, p4 = draw_two_shifted(choice[0], choice[1], choice[2], choice[3], next_div)
                        pick_one_again = np.random.random()
                        next_div = invert_for_next(next_div)
                        if pick_one_again > 0.5:
                            choice = p3
                            p5, p6 = draw_two_shifted(choice[0], choice[1], choice[2], choice[3], next_div)
                            ret_list = [p1, p4, p5, p6]
                        else:
                            choice = p4
                            p5, p6 = draw_two_shifted(choice[0], choice[1], choice[2], choice[3], next_div)
                            ret_list = [p1, p3, p5, p6]
                
            # Draw three rectangles
            if num_base == 3:
                horizontal_vertical = np.random.choice(["h", "v"])
                p1, p2, p3 = draw_three(topleft, topright, bottomright, bottomleft, horizontal_vertical)

                # Pick one and divide it into two
                pick_one = np.random.choice([1, 2, 3])
                next_div = invert_for_next(horizontal_vertical)
                if pick_one == 1:
                    choice = p1
                    p4, p5 = draw_two_shifted(choice[0], choice[1], choice[2], choice[3], next_div)
                    ret_list = [p2, p3, p4, p5]
                elif pick_one == 2:
                    choice = p2
                    p4, p5 = draw_two_shifted(choice[0], choice[1], choice[2], choice[3], next_div)
                    ret_list = [p1, p3, p4, p5]
                else:
                    choice = p3
                    p4, p5 = draw_two_shifted(choice[0], choice[1], choice[2], choice[3], next_div)
                    ret_list = [p1, p2, p4, p5]
                
                test_render(ret_list)
                    

        
        if num_panels == 5:
            # Draw 2 rectangles 
                # Pick one and divide it into two then
                    # Divide each into 2 rectangles equally
                    # Divide each into 2 rectangles unequally
                    # Pick one and divide into 2 rectangles
                        # Pick one of these two and divide that into 2 rectangles

            # Draw 3 rectangles (horizontally or vertically)
                # Pick one and divide into two
                    # Pick one of these and divide into two
                #Pick two and divide each into two

            pass

        if num_panels == 6:

            # 2 V 1 H
            # 2 H 1 V

            combo1 = dict(
                full_vertical_lines = 2,
                full_horizontal_lines = 1
            )

            combo2 = dict(
                full_vertical_lines = 1,
                full_horizontal_lines = 2
            )

            # 5 in one half
            combo3 = dict(
                full_vertical_lines = 1,
                combo_of_five = None

            )

            combo4 = dict(
                full_horizontal_lines = 1,
                combo_of_five = None
            )

            # 3 in both halves
            combo5 = dict(
                full_vertical_lines = 1,
                combo_of_three_one = None,
                combo_of_three_two = None

            )

            combo6 = dict(
                full_horizontal_lines = 1,
                combo_of_three_one = None,
                combo_of_three_two = None
            )


            # 2 in 3 parts
            combo7 = dict(
                full_vertical_lines = 3,
                half_lines = 3
            )
            combo8 = dict(
                full_horizontal_lines = 3,
                half_lines = 3
            )

            # 4 in one half 
            # 2 in another
            combo9 = dict(
                full_vertical_lines = 1,
                combo_of_four = None,
                half_line = 1

            )

            combo10 = dict(
                full_horizontal_lines = 1,
                combo_of_four = None,
                half_line = 1
            )
        if num_panels == 7:

            # Combo of 6 plus one extra half line
            pass
            
        if num_panels == 8:
            combo1 = dict(
                full_vertical_lines = 1,
                full_horizontal_lines = 3
            )

            combo2 = dict(
                full_vertical_lines = 3,
                full_horizontal_lines = 1
            )

            # Combo of 6 plus 2 extra half lines

            # 2 combos of 4
            # one combo of 2 one combo of 6
            # two combos of 3 one combo of two
            # one combo fof 5 one combo of 3


     