import numpy as np 
import random
from PIL import Image, ImageDraw, ImageFont, ImageOps
import json
import uuid
from .helpers import crop_image_only_outside
import cjkwrap

class Panel(object):

    def __init__(self, coords, name, parent, orientation, children=[], non_rect=False):

        self.x1y1 = coords[0]
        self.x2y2 = coords[1]
        self.x3y3 = coords[2]
        self.x4y4 = coords[3]
        self.name = name
        self.parent = parent

        self.coords = list(coords)
        self.non_rect = non_rect

        self.lines = [
            (self.x1y1, self.x2y2),
            (self.x2y2, self.x3y3),
            (self.x3y3, self.x4y4),
            (self.x4y4, self.x1y1)
        ]

        self.width = (self.x2y2[0] - self.x1y1[0])
        self.height = (self.x3y3[1] - self.x2y2[1])

        self.area = self.width*self.height
        self.area_proportion = round(self.area/(2400*1700), 2)

        self.children = children

        self.sliced = False

        self.orientation = orientation 

        self.no_render = False

        self.image = None

        self.speech_bubbles = []

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
        if self.non_rect:

            # Handle edge case of incorrect input
            # if len(self.coords) < 5:
                # self.coords.append(self.coords[0])

            return tuple(self.coords)
        else:

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

    def dump_data(self):
        
        if len(self.children) > 0:
            children_rec = [child.dump_data() for child in self.children]
        else:
            children_rec = []

        speech_bubbles = [bubble.dump_data() for bubble in self.speech_bubbles]
        data = dict(
            name = self.name,
            coordinates = self.coords,
            children = children_rec,
            non_rect = self.non_rect,
            sliced = self.sliced,
            no_render = self.no_render,
            image = self.image,
            speech_bubbles = speech_bubbles
        )

        return data

    def populate_children(self, data):
        
        # for panel in data['children']:
        pass

class Page(Panel):

    def __init__(self, coords, page_type, num_panels, children=[]):
        super().__init__(coords, "page", None, None, [])

        self.num_panels = num_panels
        self.page_type = page_type
        self.leaf_children = []

        # TODO: Setup naming of pages
        self.name = "Page-"+str(uuid.uuid1())

    def dump_data(self, dataset_path, dry=True):

        if len(self.children) > 0:
            children_rec = [child.dump_data() for child in self.children]
        else:
            children_rec = []

        data = dict(
            name = self.name,
            num_panels = self.num_panels,
            page_type = self.page_type,
            children = children_rec
        )   

        if not dry:
            with open(dataset_path+self.name+".json", "w+") as json_file:
                json.dump(data, json_file, indent=2)
        else:
            return json.dumps(data)
    
    def load_data(self, filename):

        pass

    def render(self, show=False):

        leaf_children = []
        if len(self.leaf_children) < 1:
            get_leaf_panels(self, leaf_children)
        else:
            leaf_children = self.leaf_children


        W = 1700
        H = 2400

        page_img = Image.new(size=(W,H), mode="L", color="white")
        draw_rect = ImageDraw.Draw(page_img)

        coords = []

        # Render panels
        for panel in leaf_children:

            img = Image.open(panel.image)

            img_array = np.asarray(img)
            crop_array = crop_image_only_outside(img_array)

            img = Image.fromarray(crop_array)

            w_rev_ratio = 1700/img.size[0]
            h_rev_ratio = 2400/img.size[1]


            #TODO Figure out how to do different types of 
            # image crops for smaller panels

            img = img.resize(
                (round(img.size[0]*w_rev_ratio),
                round(img.size[1]*h_rev_ratio))
            )

            mask = Image.new("L", (1700, 2400), 0)
            draw_mask = ImageDraw.Draw(mask)

            rect = panel.get_polygon()

            draw_mask.polygon(rect, fill=255)
            draw_rect.line(rect, fill="black", width=10) 

            page_img.paste(img, (0, 0), mask)

        # Render bubbles
        for panel in leaf_children:
            # For each bubble
                # Do for bubble
            states, bubble, mask, location = panel.speech_bubbles[0].render()
            if "inverted" in states:
                # Use mask for inverted which is inverted
                bubble_mask = ImageOps.invert(mask)
                # bubble_mask =  bubble

                # Slightly shift mask so that you get outline for bubbles
                bubble_mask = bubble_mask.resize((bubble_mask.size[0]+15, bubble_mask.size[1]+15))
                w, h = bubble.size
                crop_dims = (
                    5,5,
                    5+w, 5+h,
                )
                bubble_mask = bubble_mask.crop(crop_dims)
                page_img.paste(bubble, location, bubble_mask)
            else:
                # Slightly shift mask so that you get outline for bubbles
                bubble_mask = mask.resize((mask.size[0]+15, mask.size[1]+15))
                w, h = bubble.size
                crop_dims = (
                    5,5,
                    5+w, 5+h,
                )
                bubble_mask = bubble_mask.crop(crop_dims)
                page_img.paste(bubble, location, bubble_mask)

        if show:
            page_img.show()
        else:
            return page_img

class SpeechBubble(object):
    def __init__(self, texts, font, speech_bubble, writing_areas, new_area, location):

        self.texts = texts
        self.font = font
        self.speech_bubble = speech_bubble
        self.writing_areas = writing_areas
        self.transform = None
        self.resize_to = new_area
        self.location = location
        
        
        # 1 in 100 chance
        if np.random.random() < 0.01:
            self.text_orientation = "ltr"
        else:
            self.text_orientation = "ttb"

    def render(self):

        bubble = Image.open(self.speech_bubble).convert("L")
        mask = bubble.copy()

        write = ImageDraw.Draw(bubble)

        # Set variable font size
        min_font_size = 54
        max_font_size = 72
        current_font_size = np.random.randint(min_font_size,
                                              max_font_size
                                              )

        font = ImageFont.truetype(self.font,current_font_size)

        # transforms
            # invert (1 in 20)
            # flip horizontal
            # flip vertical
            # stretch x or y
            # shrink x or y
            # shear

        transforms = [
            "invert",
            "flip horizontal",
            "flip vertical",
            "rotate",
            "stretch x",
            "stretch y",
            "shrink",
            "grow"
        ]

        self.transforms = np.random.choice(transforms, 3)

        w, h = bubble.size

        # 1 in 50 chance of no transformation
        # if np.random.rand() < 0.98:
        # for transform in chosen_transforms:
        states = []
        transform = ""
        # transform = "flip vertical"
        if transform == "invert":
            states.append("inverted")
            bubble = ImageOps.invert(bubble)
        
        elif transform == "flip vertical": 
            bubble = ImageOps.flip(bubble)
            # TODO: vertically flip box coordinates
            new_writing_areas = []

        
        elif transform == "flip horizontal":
            bubble = ImageOps.mirror(bubble)
            # TODO: horizontally flip box coordinates
        
        elif transform == "stretch x":
            # TODO stretch box
            pass

        elif transform == "stretch y":
            # TODO stretch box
            pass

        elif transform == "shrink":
            # TODO shrink box
            pass
        elif transform == "grow":
            pass

        elif transform == "rotate":
            pass
        
        # Write text into bubble
        if "inverted" in states:
            fill_type = "white"
        else:
            fill_type = "black"

        for i, area in enumerate(self.writing_areas):
            og_width = area['original_width']
            og_height = area['original_height']

            # Convert from percentage to actual values
            px_width =  (area['width']/100)*og_width
            px_height =  (area['height']/100)*og_height

            og_x = ((area['x']/100)*og_width)
            og_y = ((area['y']/100)*og_height)

            # Padded
            x = og_x + 20
            y = og_y + 20

            # More padding
            max_x = px_width - 20
            max_y = px_height - 20

            text = self.texts[i]['Japanese']
            text = text+text+text+text+text
            text_segments = [text]
            size = font.getsize(text)


            if self.text_orientation == "ttb":
            
                # Setup vertical wrapping
                avg_height = size[0]/len(text)
                max_chars = int((px_height//avg_height))
                if size[0] > px_height:
                    # Using specialized wrapping library
                    text_segments = cjkwrap.wrap(text, width=max_chars)

                text_max_w = len(text_segments)*size[1]
                
                is_fit = False

                # Horizontal wrapping
                # Reduce font or remove words till text fits
                while not is_fit:     
                    if text_max_w > px_width:
                        if current_font_size > min_font_size: 
                            current_font_size -= 1
                            font = ImageFont.truetype(self.font, current_font_size)
                            size = font.getsize(text)
                            avg_height = size[0]/len(text)
                            max_chars = int((max_y//avg_height))
                            text_segments = cjkwrap.wrap(text, width=max_chars)
                            text_max_w = len(text_segments)*size[1]
                        else:
                            text_segments.pop()
                            text_max_w = len(text_segments)*size[1]
                    else:
                        is_fit = True

            # if text left to right
            else:
                pass
                # Setup horizontal wrapping
                avg_width = size[0]/len(text)
                max_chars = int((px_width//avg_width))
                if size[0] > px_width:
                    # Using specialized wrapping library
                    text_segments = cjkwrap.wrap(text, width=max_chars)
                
                # Setup vertical wrapping
                text_max_h = len(text_segments)*size[1]
                is_fit = False
                while not is_fit:
                    if text_max_h > px_height:
                        if current_font_size > min_font_size:
                            current_font_size -=1
                            font = ImageFont.truetype(self.font, current_font_size)
                            size = font.getsize(text)
                            avg_width = size[0]/len(text)
                            max_chars = int((px_width//avg_width))
                            text_segments = cjkwrap.wrap(text, width=max_chars)
                            text_max_h = len(text_segments)*size[1]
                        else:
                            text_segments.pop()
                            text_max_h = len(text_segments)*size[1]
                    else:
                        is_fit = True

            # Center bubble x axis
            cbx = og_x + (px_width/2)
            cby = og_y + (px_height/2)

            # Render text
            for i, text in enumerate(text_segments):
                if self.text_orientation == 'ttb':
                    rx = (cbx + text_max_w/2) - ((len(text_segments) - i)*size[1])
                    ry = y
                else:
                    seg_size = font.getsize(text)
                    rx = cbx - seg_size[0]/2
                    ry = (cby + (len(text_segments)*size[1])/2) - ((len(text_segments) - i)*size[1])
                write.text((rx, ry),
                            text,
                            font=font,
                            language="ja",
                            fill="black",
                            direction=self.text_orientation)

        # reisize bubble
        aspect_ratio = h/w
        new_height = round(np.sqrt(self.resize_to/aspect_ratio))
        new_width = round(new_height * aspect_ratio)
        bubble = bubble.resize((new_height, new_width))
        mask = mask.resize((new_height, new_width))
        # bubble.show()

        # Make sure bubble doesn't bleed the page 
        x1, y1 = self.location
        x2 = x1 +bubble.size[0]
        y2 = y1 +bubble.size[1]

        if x2 > 1700:
            x1 = x1 - (x2-1700)
        if y2 > 2400:
            y1 = y1 - (y2-1700)
        
        self.location = (x1, y1)
        return states, bubble, mask, self.location

