### Page rendering
page_width = 1700
page_height= 2400

page_size = (page_width, page_height)

output_format = ".png"

boundary_width = 10

### Font coverage
# How many characters of the dataset should the font files support
font_character_coverage = 0.80


### Panel Drawing

## Panel ratios

num_pages_ratios = {
    1:0.125,
    2:0.125,
    3:0.125,
    4:0.125,
    5:0.125,
    6:0.125,
    7:0.125,
    8:0.125
}

vertical_horizontal_ratios = {
    "v": 0.1,
    "h": 0.1,
    "vh": 0.8
}

## Panel transform chance

panel_transform_chance = 0.90

## Panel shrinking

panel_shrink_amount = -25

## Panel removal

panel_removal_chance = 0.01
panel_removal_max = 2

## Background adding
background_add_chance = 0.01

## Speech bubbles
max_speech_bubbles_per_panel = 3
bubble_to_panel_area_max_ratio = 0.4

## Transformations

## Slicing
double_slice_chance = 0.25
slice_minimum_panel_area = 0.2
center_side_ratio = 0.7

## Box transforms
box_transform_panel_chance = 0.1
panel_box_trapezoid_ratio = 0.5

# How much at most should the trapezoid/rhombus start from
# as a ratio of the smallest panel's width or height
trapezoid_movement_proportion_limit = 50  
rhombus_movement_proportion_limit = 50  

full_page_movement_proportion_limit = 25
