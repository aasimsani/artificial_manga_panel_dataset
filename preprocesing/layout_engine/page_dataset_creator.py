from PIL import Image, ImageDraw
import numpy as np 
import math

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
    page = Image.new(size=(W,H), mode="L", color="white")
    draw_rect = ImageDraw.Draw(page)

    for rect in dims:
        draw_rect.rectangle(rect, fill=None, outline="red", width=10)

    page.show()

def create_page_metadata():


    # Select page type
    # Select number of panels on the page
        # between 1 and 8
    # Select panel boundary type
    # Select panel boundary widths

    # Each page is a 2x4 grid

    # if page only h then all 
    # if only v then fit simply
    # if vh then rescale panels and fit randomly
        # Randomly assign each panel to be a v or h
        # For the chosen number of panels
            # Spawn a panel center randomly on the page 
            # Claim the grid box for this panel and
            # so the next one can only spawn on other grid
            # boxes
        # Once you've spawned the panels expand their boundaries
        # at the same time till you hit the page edge or another
        # panel

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
                ph = round(panel_height_default*(1 - (change/100)), 2)
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
        panel_width_default = 425
        panel_height_default = 600

        max_num_panels = 8
        num_panels = np.random.randint(2, max_num_panels+1)

        # Initalize
        panel_sizes = {}
        panel_locations = {}

        for panel in range(0, num_panels):
            panel_sizes[panel] = [panel_width_default, panel_height_default]
            loc = np.random.randint(0, max_num_panels)
            panel_locations[panel] = loc


        vertical_line_movement = {}
        horizontal_line_movement = {}

        num_vert_lines = 4
        num_hor_lines = 3

        # Move vertical lines
        for line in range(0, num_vert_lines):
            change = np.random.randint(-25, 25)
            vertical_line_movement[line] = change/100

        # Move horizontal lines
        for line in range(0, num_hor_lines):
            change = np.random.randint(-50, 50)
            horizontal_line_movement[line] = change/100


        # Grow into free panel
        free_panels = []
        for panel in panel_locations:
            panel_loc = panel_locations[panel]
            below = panel_loc + 2
            if panel_loc % 2:
                besides = panel_loc  + 1
            else:
                besides = panel_loc - 1
            
  
