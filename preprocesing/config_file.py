### Page rendering
page_width = 1700
page_height= 2400

page_size = (page_width, page_height)

output_format = ".png"

boundary_width = 20

### Font coverage
# How many characters of the dataset should the font files support
font_character_coverage = 0.80


### Panel Drawing

## Panel srhinking

panel_shrink_amount = -25



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
