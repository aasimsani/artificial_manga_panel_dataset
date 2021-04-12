from PIL import Image, ImageDraw
import numpy as np 
import math
import time
from copy import deepcopy

def create_single_panel_metadata():

    # Coords
    # Dims
    # 
    pass


# TODO: Figure out page type distributions

def test_render(dims):

    W = 1700
    H = 2400
    print(dims)
    page = Image.new(size=(W,H), mode="L", color="black")
    draw_rect = ImageDraw.Draw(page)

    for rect in dims:
        draw_rect.rectangle(rect, fill=None, outline="white", width=20)

    page.show()

def create_page_metadata():


    # Select page type
    # Select number of panels on the page
        # between 1 and 8
    # Select panel boundary type
    # Select panel boundary widths

    # Each page is a 2x4 grid

    panel_dims = []

    layout_type = "vh"
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
    

    # TODO: see if you want to reuse this
    elif layout_type == "vh":
        panel_width_default = 850
        panel_height_default = 600

        max_num_panels = 8
        num_panels = np.random.randint(2, max_num_panels+1)

        # Initalize
        panel_sizes = {}
        panel_locations = {}
        free_panels = list(range(0, max_num_panels))

        # Currentlly all are free
        for panel in free_panels:
            panel_sizes[panel] = [panel_width_default, panel_height_default]

        for panel in range(0, num_panels):
            loc = np.random.choice(free_panels)
            panel_locations[panel] = [loc]
            free_panels.remove(loc)


        # TODO: Figure out formula for this eventually
        num_vert_lines = 4
        num_hor_lines = 3

        # Move vertical lines
        for line in range(0, num_vert_lines):
            change = np.random.randint(-50, 50)
            change = change/100

            # TODO: Find formulaic version for this
            # 0 corresponds to panel 0 and 1
            # 1 corresponds to panel 2 and 3
            # 2 corresponds to panel 4 and 5
            # 3 corresponds to panel 6 and 7

            p1i = line*2 
            p2i = p1i + 1
            p1 = panel_sizes[p1i]
            p2 = panel_sizes[p2i]

            p1w = round(p1[0]*(1-change), -1)
            p2w = p2[0]*2 - p1w

            panel_sizes[p1i] = [p1w, p1[1]] 
            panel_sizes[p2i] = [p2w, p2[1]]

        # Move horizontal lines in 2 broad sets
        for line in range(0, 3):
            change = np.random.randint(-75, 75)
            change = change/100

            if line == 1:
                line = 4

            p1i = line
            p2i = line + 1
            p3i = line + 2
            p4i = line + 3

            p1 = panel_sizes[p1i]
            p2 = panel_sizes[p2i]
            p3 = panel_sizes[p3i]
            p4 = panel_sizes[p4i]

            p1h = round(p1[1]*(1-change), -1)
            p2h = round(p2[1]*(1-change), -1)
            p3h = panel_height_default*2 - p1h  
            p4h = panel_height_default*2 - p2h 

            panel_sizes[p1i] = [p1[0], p1h] 
            panel_sizes[p2i] = [p2[0], p2h]
            panel_sizes[p3i] = [p3[0], p2h]
            panel_sizes[p4i] = [p4[0], p2h]
                    

        height_sum_left = 0.0
        height_sum_right = 0.0
        for idx, panel in panel_sizes.items():
            if idx % 2:
                height_sum_left += panel[1]
            else:
                height_sum_right += panel[1]
        
        # Since heights have > 1 dependency in terms of growing instead of writing a smart
        # algorithm to account for it we just renormalize the dims
        extra_height_left = (2400 - height_sum_left)/4
        extra_height_right = (2400 - height_sum_right)/4
        for idx, panel in panel_sizes.items():
            if idx % 2:
                new_height = panel[1] + extra_height_left 
            else:
                new_height = panel[1] + extra_height_right
            panel_sizes[idx] = [panel[0], new_height]

        # Convert to coords - also makes merging faster 
        panel_coords = []
        current_x_axis_location = 0.0 

        above_left_y_axis_location = 0.0
        above_right_y_axis_location = 0.0

        for num, panel in panel_sizes.items():
            if current_x_axis_location == 1700:
                current_x_axis_location = 0.0

            x1 = current_x_axis_location
            x2 = current_x_axis_location + panel[0] 
            current_x_axis_location = x2

            if num % 2:
                y1 = above_left_y_axis_location 
                y2 = above_left_y_axis_location + panel[1]
                above_left_y_axis_location = y2
            else:
                y1 = above_right_y_axis_location
                y2 = above_right_y_axis_location + panel[1]
                above_right_y_axis_location = y2

            coord = ((x1, y1), (x2, y2))
            panel_coords.append(coord)
        

        test_render(panel_coords)
            
  
