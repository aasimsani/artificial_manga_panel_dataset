from PIL import Image, ImageDraw
import numpy as np 
import math
import time
from copy import deepcopy
import random

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

def draw_n_shifted(n, topleft, topright, bottomright, bottomleft, horizontal_vertical, shifts=[]):

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

        polys = []

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

                poly = (x1y1, x2y2, x3y3, x4y4, x1y1)
                polys.append(poly)
        
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

                poly = (x1y1, x2y2, x3y3, x4y4, x1y1)
                polys.append(poly)

        return polys

def draw_n(n, topleft, topright, bottomright, bottomleft, horizontal_vertical):

        polys = []
        
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

                poly = (x1y1, x2y2, x3y3, x4y4, x1y1)
                polys.append(poly)
        
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

                poly = (x1y1, x2y2, x3y3, x4y4, x1y1)
                polys.append(poly)

        return polys

def draw_four(topleft, topright, bottomright, bottomleft, horizontal_vertical):

    if horizontal_vertical == "h":
        r1x1y1 = topleft
        r1x2y2 = topright
        r1x3y3 = (bottomright[0], topright[1] + (bottomright[1]- topright[1])/4)
        r1x4y4 = (bottomleft[0], topleft[1] + (bottomleft[1] - topleft[1])/4)

        poly1 = (r1x1y1, r1x2y2, r1x3y3, r1x4y4, r1x1y1)

        r2x1y1 = (bottomleft[0], topleft[1] + (bottomleft[1] - topleft[1])/4)
        r2x2y2 = (bottomright[0], topright[1] + (bottomright[1]- topright[1])/4)
        r2x3y3 = (bottomright[0], topright[1] + (bottomright[1]- topright[1])*(2/4))
        r2x4y4 = (bottomleft[0], topleft[1] + (bottomleft[1] - topleft[1])*(2/4))

        poly2 = (r2x1y1, r2x2y2, r2x3y3, r2x4y4, r2x1y1)

        r3x1y1 = (bottomleft[0], topleft[1] + (bottomleft[1] - topleft[1])*(2/4))
        r3x2y2 = (bottomright[0], topright[1] + (bottomright[1]- topright[1])*(2/4))
        r3x3y3 = (bottomright[0], topright[1] + (bottomright[1]- topright[1])*(3/4))
        r3x4y4 = (bottomleft[0], topleft[1] + (bottomleft[1] - topleft[1])*(3/4))

        poly3 = (r3x1y1, r3x2y2, r3x3y3, r3x4y4, r3x1y1)

        r4x1y1 = (bottomleft[0], topleft[1] + (bottomleft[1] - topleft[1])*(3/4))
        r4x2y2 = (bottomright[0], topright[1] + (bottomright[1]- topright[1])*(3/4))
        r4x3y3 = bottomright
        r4x4y4 = bottomleft 

        poly4 = (r4x1y1, r4x2y2, r4x3y3, r4x4y4, r4x1y1)

    
    if horizontal_vertical == "v":
        r1x1y1 = topleft
        r1x2y2 = (topright[0]/4, topright[1])
        r1x3y3 = (bottomright[0]/4, bottomright[1])
        r1x4y4 = bottomleft

        poly1 = (r1x1y1, r1x2y2, r1x3y3, r1x4y4, r1x1y1)

        r2x1y1 = (topright[0]/4, topright[1])
        r2x2y2 = (topright[0]*(2/4), topright[1])
        r2x3y3 = (bottomright[0]*(2/4), bottomright[1])
        r2x4y4 = (bottomright[0]/4, bottomright[1])

        poly2 = (r2x1y1, r2x2y2, r2x3y3, r2x4y4, r2x1y1)

        r3x1y1 = (topright[0]*(2/4), topright[1])
        r3x2y2 = (topright[0]*(3/4), topright[1])
        r3x3y3 = (bottomright[0]*(3/4), bottomright[1])
        r3x4y4 = (bottomright[0]*(2/4), bottomright[1])

        poly3 = (r3x1y1, r3x2y2, r3x3y3, r3x4y4, r3x1y1)

        r4x1y1 = (topright[0]*(3/4), topright[1])
        r4x2y2 = topright
        r4x3y3 = bottomright
        r4x4y4 = (bottomright[0]*(3/4), bottomright[1])

        poly4 = (r4x1y1, r4x2y2, r4x3y3, r4x4y4, r4x1y1)
    
    return poly1, poly2, poly3, poly4

# TODO: Add a shifting version of this
def draw_three(topleft, topright, bottomright, bottomleft, horizontal_vertical):

    if horizontal_vertical == "h":
        r1x1y1 = topleft
        r1x2y2 = topright
        r1x3y3 = (bottomright[0], topright[1] + (bottomright[1]- topright[1])/3)
        r1x4y4 = (bottomleft[0], topleft[1] + (bottomleft[1] - topleft[1])/3)

        poly1 = (r1x1y1, r1x2y2, r1x3y3, r1x4y4, r1x1y1)

        r2x1y1 = (bottomleft[0], topleft[1] + (bottomleft[1] - topleft[1])/3)
        r2x2y2 = (bottomright[0], topright[1] + (bottomright[1]- topright[1])/3)
        r2x3y3 = (bottomright[0], topright[1] + (bottomright[1]- topright[1])*(2/3))
        r2x4y4 = (bottomleft[0], topleft[1] + (bottomleft[1] - topleft[1])*(2/3))

        poly2 = (r2x1y1, r2x2y2, r2x3y3, r2x4y4, r2x1y1)

        r3x1y1 = (bottomleft[0], topleft[1] + (bottomleft[1] - topleft[1])*(2/3))
        r3x2y2 = (bottomright[0], topright[1] + (bottomright[1]- topright[1])*(2/3))
        r3x3y3 = bottomright
        r3x4y4 = bottomleft 

        poly3 = (r3x1y1, r3x2y2, r3x3y3, r3x4y4, r3x1y1)

    
    if horizontal_vertical == "v":
        r1x1y1 = topleft
        r1x2y2 = (topright[0]/3, topright[1])
        r1x3y3 = (bottomright[0]/3, bottomright[1])
        r1x4y4 = bottomleft

        poly1 = (r1x1y1, r1x2y2, r1x3y3, r1x4y4, r1x1y1)

        r2x1y1 = (topright[0]/3, topright[1])
        r2x2y2 = (topright[0]*(2/3), topright[1])
        r2x3y3 = (bottomright[0]*(2/3), bottomright[1])
        r2x4y4 = (bottomright[0]/3, bottomright[1])

        poly2 = (r2x1y1, r2x2y2, r2x3y3, r2x4y4, r2x1y1)

        r3x1y1 = (topright[0]*(2/3), topright[1])
        r3x2y2 = topright
        r3x3y3 = bottomright
        r3x4y4 = (bottomright[0]*(2/3), bottomright[1])

        poly3 = (r3x1y1, r3x2y2, r3x3y3, r3x4y4, r3x1y1)
    
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
        r1x3y3 = (bottomright[0], topright[1] + (bottomright[1] - topright[1])*shift)
        r1x4y4 = (bottomleft[0], topleft[1] + (bottomleft[1] - topleft[1])*shift)

        poly1 = (r1x1y1, r1x2y2, r1x3y3, r1x4y4, r1x1y1)

        r2x1y1 = (bottomleft[0], topleft[1] + (bottomleft[1] - topleft[1])*shift)
        r2x2y2 = (bottomright[0], topright[1] + (bottomright[1] - topright[1])*shift)
        r2x3y3 = bottomright
        r2x4y4 = bottomleft

        poly2 = (r2x1y1, r2x2y2, r2x3y3, r2x4y4, r2x1y1)
    
    if horizontal_vertical == "v":
        
        r1x1y1 = topleft
        r1x2y2 = (topleft[0] + (topright[0] - topleft[0])*shift, topright[1])
        r1x3y3 = (bottomleft[0] + (bottomright[0] - bottomleft[0])*shift, bottomright[1])
        r1x4y4 = bottomleft

        poly1 = (r1x1y1, r1x2y2, r1x3y3, r1x4y4, r1x1y1)

        r2x1y1 = (topleft[0] + (topright[0] - topleft[0])*shift, topright[1])
        r2x2y2 = topright
        r2x3y3 = bottomright
        r2x4y4 = (bottomleft[0] + (bottomright[0] - bottomleft[0])*shift, bottomright[1])

        poly2 = (r2x1y1, r2x2y2, r2x3y3, r2x4y4, r2x1y1)
   
    return poly1, poly2

def invert_for_next(current):
    if current == "h":
        return "v"
    else:
        return "h"

def choose_and_return(choices):

    # Shuffle for random picking
    random.shuffle(choices)

    # Pop one after shuffling
    choice = choices.pop(0)

    return choice, choices

def create_page_metadata():

    # Select page type
    # Select number of panels on the page
        # between 1 and 8
    # Select panel boundary type
    # Select panel boundary widths


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
    # Polygons to return
    ret_list = []

    layout_type = "vh"

# TODO: Fit in getting black pages sperately
    if layout_type == "v":
        max_num_panels = 4

        num_panels = np.random.randint(2, max_num_panels+1)
        ret_list = draw_n_shifted(num_panels, *dims, "v")
        
    elif layout_type == "h":
        max_num_panels = 6

        num_panels = np.random.randint(2, max_num_panels+1)
        ret_list = draw_n_shifted(num_panels, *dims, "h")
    
    elif layout_type == "vh":
        
        max_num_panels = 8
        num_panels = np.random.randint(2, max_num_panels+1)
        
        if num_panels == 2:
            # Draw 2 rectangles
                # vertically or horizontally
            horizontal_vertical = np.random.choice(["h", "v"])
            p1, p2 = draw_two_shifted(*dims, horizontal_vertical)
            ret_list = [p1, p2]
    
        if num_panels == 3:
            # Draw 2 rectangles
                # Vertically or Horizontally

            horizontal_vertical = np.random.choice(["h", "v"])
            p1, p2 = draw_two_shifted(*dims, horizontal_vertical)

            next_div = invert_for_next(horizontal_vertical)

            # Pick one and divide it into 2 rectangles
            choice, left_choices = choose_and_return([p1, p2])

            p3, p4 = draw_two_shifted(*choice[0:4], next_div)
            ret_list = left_choices + [p3, p4]

        if num_panels == 4:
            horizontal_vertical = np.random.choice(["h", "v"])
            type_choice = np.random.choice(["eq", "uneq", "div", "trip"]) 

            # Draw two rectangles 
            if type_choice == "eq":
                p1, p2 = draw_two_shifted(*dims, horizontal_vertical, shift=0.5)
                next_div = invert_for_next(horizontal_vertical)

                # Divide each into 2 rectangles equally
                shift_min = 25
                shift_max = 75
                shift = np.random.randint(shift_min, shift_max)
                shift = shift/100 

                p3, p4 = draw_two_shifted(*p1[0:4], next_div, shift)
                p5, p6 = draw_two_shifted(*p2[0:4], next_div, shift)
                ret_list = [p3, p4, p5, p6]

            # Divide each into 2 rectangles unequally
            elif type_choice == "uneq":
                p1, p2 = draw_two_shifted(*dims, horizontal_vertical, shift=0.5)
                next_div = invert_for_next(horizontal_vertical)

                p3, p4 = draw_two_shifted(*p1[0:4], next_div)
                p5, p6 = draw_two_shifted(*p2[0:4], next_div)
                ret_list = [p3, p4, p5, p6]

            elif type_choice == "div":
                p1, p2 = draw_two_shifted(*dims, horizontal_vertical, shift=0.5)
                next_div = invert_for_next(horizontal_vertical)
                pick_one = np.random.random()
                # Pick one and divide into 2 rectangles
                choice1, left_choices1 = choose_and_return([p1, p2]) 
                p3, p4 = draw_two_shifted(*choice1[0:4], next_div)

                # Pick one of these two and divide that into 2 rectangles
                choice2, left_choices2 = choose_and_return([p3, p4])
                next_div = invert_for_next(next_div)
                p5, p6 = draw_two_shifted(*choice2[0:4], next_div)

                ret_list = left_choices1 + left_choices2 + [p5, p6]
            
            # Draw three rectangles
            elif type_choice == "trip":
                p1, p2, p3 = draw_three(*dims, horizontal_vertical)

                # Pick one and divide it into two
                choice, left_choices = choose_and_return([p1, p2, p3])
                next_div = invert_for_next(horizontal_vertical)
                p4, p5 = draw_two_shifted(*choice[0:4], next_div)

                ret_list = left_choices + [p4, p5]
        
        if num_panels == 5:

            # Draw two rectangles 
            horizontal_vertical = np.random.choice(["h", "v"])
            
            type_choice = np.random.choice(["eq", "uneq", "div", "twotwothree", "threetwotwo", "fourtwoone"])
            if type_choice == "eq" or type_choice == "uneq":

                p1, p2 = draw_two_shifted(*dims, horizontal_vertical, shift=0.5)
                next_div = invert_for_next(horizontal_vertical)

                # Pick one and divide it into two then
                choice, left_choices = choose_and_return([p1, p2])
                p3, p4 = draw_two_shifted(*choice[0:4], next_div)                    

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
                p5, p6 = draw_two_shifted(*p3[0:4], next_div, shift=set_shift)
                p7, p8 = draw_two_shifted(*p4[0:4], next_div, shift=set_shift)
                ret_list = left_choices + [p5, p6, p7, p8]


            # Draw two rectangles
            elif type_choice == "div":
                p1, p2 = draw_two_shifted(*dims, horizontal_vertical, shift=0.5)
                next_div = invert_for_next(horizontal_vertical)

                # Divide both equally
                p3, p4 = draw_two_shifted(*p1[0:4], next_div)
                p5, p6 = draw_two_shifted(*p2[0:4], next_div)

                # Pick one of all of them and divide into two
                choice, left_choices = choose_and_return([p3, p4, p5, p6])
                next_div = invert_for_next(next_div)
                p7, p8 = draw_two_shifted(*choice[0:4], horizontal_vertical=next_div, shift=0.5)

                ret_list = left_choices + [p7, p8]
        
            # Draw two rectangles
            elif type_choice == "twotwothree":
                
                p1, p2 = draw_two_shifted(*dims, horizontal_vertical, shift=0.5)
                next_div = invert_for_next(horizontal_vertical)

                # Pick which one gets 2 and which gets 3 
                choice, left_choices = choose_and_return([p1, p2])
                other = left_choices[0]

                # Divide one into 2
                next_div = invert_for_next(horizontal_vertical)
                p3, p4 = draw_two_shifted(*choice[0:4], next_div)

                # Divide other into 3
                p5, p6, p7 = draw_three(*other[0:4], next_div)

                ret_list = [p3, p4, p5, p6, p7]

            # Draw 3 rectangles (horizontally or vertically)
            elif type_choice == "threetwotwo":

                p1, p2, p3 = draw_three(*dims, horizontal_vertical)
                next_div = invert_for_next(horizontal_vertical)

                choice1, left_choices1 = choose_and_return([p1, p2, p3])
                choice2, left_choices2 = choose_and_return(left_choices1)

                # Pick two and divide each into two
                p4, p5 = draw_two_shifted(*choice1[0:4], next_div)
                p6, p7 = draw_two_shifted(*choice2[0:4], next_div)

                ret_list = left_choices2 + [p4, p5, p6, p7]
            
            # Draw 4 rectangles vertically
            elif type_choice == "fourtwoone":
                panels = draw_n(4, *dims, horizontal_vertical)

                # Pick one and divide into two
                choice, left_choices = choose_and_return(panels)
                next_div = invert_for_next(horizontal_vertical)
                p5, p6 = draw_two_shifted(*choice[0:4], next_div)

                ret_list = left_choices + [p5, p6]


        if num_panels == 6:
            
            type_choice = np.random.choice(["tripeq", "tripuneq", "twofourtwo","twothreethree", "fourtwo"])

            horizontal_vertical = np.random.choice(["v", "h"])

            # Draw 3 rectangles (V OR H)
            if type_choice == "tripeq" or type_choice == "tripuneq":
                panels = draw_n_shifted(3, *dims, horizontal_vertical)
                # Split each equally
                if type_choice == "tripeq":
                    shift = np.random.randint(25, 75)
                    shift = shift/100
                # Split each unequally
                else:
                    shift = None

                next_div = invert_for_next(horizontal_vertical)
                for panel in panels:
                    p1, p2 = draw_two_shifted(*panel[0:4], next_div, shift=shift)
                    ret_list += [p1, p2]

            # Draw 2 rectangles
            elif type_choice == "twofourtwo":
                p1, p2 = draw_two_shifted(*dims, horizontal_vertical)
                # Split into 4 one half 2 in another
                next_div = invert_for_next(horizontal_vertical)
                ret_list += draw_n_shifted(4, *p1[0:4], next_div)
                ret_list += draw_two_shifted(*p2[0:4], next_div)

            # Draw 2 rectangles
            elif type_choice == "twothreethree":
                # Split 3 in each
                panels = draw_two_shifted(*dims, horizontal_vertical)
                next_div = invert_for_next(horizontal_vertical)

                for panel in panels:
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


                    split_panels = draw_n_shifted(3, *panel[0:4], next_div, shifts=normalized_shifts) 
                    ret_list += split_panels

            # Draw 4 rectangles
            elif type_choice == "fourtwo": 
                panels = draw_n_shifted(4, *dims, horizontal_vertical)

                # Split two of them
                choice1, left_choices1 = choose_and_return(panels)
                choice2, left_choices2 = choose_and_return(left_choices1)

                next_div = invert_for_next(horizontal_vertical)
                split1 = draw_two_shifted(*choice1[0:4], next_div)
                split2 = draw_two_shifted(*choice2[0:4], next_div)

                ret_list = left_choices2 + list(split1) + list(split2)

        if num_panels == 7:
            
            types = ["twothreefour", "threethreetwotwo", "threefourtwoone","threethreextwoone","fourthreextwo"]
            type_choice = np.random.choice(types)

            # Draw two split 3-4 - HV
            if type_choice == "twothreefour":
                horizontal_vertical = np.random.choice(["h", "v"])

                panels = draw_two_shifted(*dims, horizontal_vertical, shift=0.5)

                choice, left_choices = choose_and_return(list(panels))
                other = left_choices[0]

                next_div = invert_for_next(horizontal_vertical)
                
                split1 = draw_n_shifted(4, *choice[0:4], next_div)

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

                split2 = draw_n_shifted(3, *other[0:4], next_div, shifts=normalized_shifts) 

                ret_list = list(split1) + list(split2)

            # Draw 3 split 3-2-2 - H only
            elif type_choice == "threethreetwotwo":
                panels = draw_three(*dims, "h")

                choice, left_choices = choose_and_return(list(panels))

                split1 = draw_n_shifted(3, *choice[0:4], "v")
                split2 = draw_two_shifted(*left_choices[0][0:4], "v")
                split3 = draw_two_shifted(*left_choices[1][0:4], "v")

                ret_list = list(split1) + list(split2) + list(split3)

            # Draw 3 split 4-2-1 - H only
            elif type_choice == "threefourtwoone":
                panels = draw_three(*dims, "h")
                choice, left_choices = choose_and_return(list(panels))

                split1 = draw_n_shifted(4, *choice[0:4], "v")
                split2 = draw_two_shifted(*left_choices[0][0:4], "v")

                ret_list = left_choices + split1 +list(split2)

            # Draw 3 split 3-3-1 - H
            elif type_choice == "threethreextwoone":
                panels = draw_three(*dims, "h")
                choice, left_choices = choose_and_return(list(panels))

                split1 = draw_n_shifted(3, *choice[0:4], "v")
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

                split2 = draw_n_shifted(3, *left_choices[0][0:4], "v", shifts=normalized_shifts)

                ret_list = left_choices + split1 + split2

            # Draw 4 split 3x2 - HV
            elif type_choice == "fourthreextwo":
                horizontal_vertical = np.random.choice(["h", "v"])
                panels = draw_n(4, *dims, horizontal_vertical)

                choice, left_choices = choose_and_return(panels)

                next_div = invert_for_next(horizontal_vertical)
                for panel in left_choices:
                    split = draw_two_shifted(*panel[0:4], next_div)
                    ret_list += list(split)

                ret_list += choice
            
        if num_panels == 8:
            types = ["fourfourxtwoeq", "fourfourxtwouneq", "threethreethreetwo", "threefourtwotwo", "threethreefourone"]
            type_choice = np.random.choice(types) 

            # Draw 4 x 2
            if type_choice == "fourfourxtwoeq" or type_choice =="fourfourxtwouneq":
                # panels = draw_n_shifted(4, *dims, "h")
                panels = draw_n(4, *dims, "h")
                # Equal 
                if type_choice == "fourfourxtwoeq":
                    shift_min = 25
                    shift_max = 75
                    shift = np.random.randint(shift_min, shift_max) 
                    set_shift = shift/100 
                # Unequal
                else:
                    set_shift = None

                for panel in panels:
                    
                    split = draw_two_shifted(*panel[0:4], "v",shift=set_shift)
                    ret_list += list(split)
            
            if type_choice in types[2:]:
                # Draw three - H
                panels = draw_n(3, *dims, "h")

                # Draw 3 3-3-2 - H
                if type_choice == "threethreethreetwo":
                    choice, left_choices = choose_and_return(panels)
                    two_split = draw_two_shifted(*choice[0:4], "v")

                    ret_list += list(two_split)
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

                        split = draw_n_shifted(3, *panel[0:4], "v", shifts=normalized_shifts)
                        ret_list += split

                # Draw 3 4-2-2 - H
                elif type_choice == "threefourtwotwo":
                    choice, left_choices = choose_and_return(panels)

                    four_split = draw_n_shifted(4, *choice[0:4], "v")

                    ret_list += four_split

                    for panel in left_choices:
                        split = draw_two_shifted(*panel[0:4], "v")
                        ret_list += list(split)
                    
                # Draw 3 3-4-1 - H 

                elif type_choice == "threethreefourone":
                    choice, left_choices = choose_and_return(panels)
                    other = left_choices[0]

                    # 1
                    ret_list += left_choices[1]

                    #3
                    three_split = draw_n_shifted(3, *choice[0:4], "v")

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
                    
                    four_split = draw_n_shifted(4, *other[0:4], "v", shifts=normalized_shifts)

                    ret_list += three_split + four_split


    test_render(ret_list)
     