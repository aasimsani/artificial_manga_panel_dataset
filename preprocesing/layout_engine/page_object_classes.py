import numpy as np 
import random
from PIL import Image, ImageDraw, ImageFont, ImageOps
import json
import uuid
from .helpers import crop_image_only_outside
import cjkwrap
from .helpers import get_leaf_panels
from .. import config_file as cfg

class Panel(object):

    def __init__(self, coords, name, parent, orientation, children=[], non_rect=False):

        coords = [tuple(c) for c in coords]        

        self.x1y1 = coords[0]
        self.x2y2 = coords[1]
        self.x3y3 = coords[2]
        self.x4y4 = coords[3]

        self.lines = [
            (self.x1y1, self.x2y2),
            (self.x2y2, self.x3y3),
            (self.x3y3, self.x4y4),
            (self.x4y4, self.x1y1)
        ]

        self.name = name
        self.parent = parent

        self.coords = coords
        self.non_rect = non_rect

        

        self.width = float((self.x2y2[0] - self.x1y1[0]))
        self.height = float((self.x3y3[1] - self.x2y2[1]))

        self.area = float(self.width*self.height)
        self.area_proportion = int(round(self.area/(cfg.page_height*cfg.page_width), 2))

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
            orientation = self.orientation,
            children = children_rec,
            non_rect = self.non_rect,
            sliced = self.sliced,
            no_render = self.no_render,
            image = self.image,
            speech_bubbles = speech_bubbles
        )

        return data

    def load_data(self, data):

        self.sliced = data['sliced']
        self.no_render = data['no_render']
        self.image = data['image']

        if len(data['speech_bubbles']) > 0:
            for speech_bubble in data['speech_bubbles']:
                bubble = SpeechBubble(
                            texts=speech_bubble['texts'],
                            texts_indices=speech_bubble['texts_indices'],
                            font=speech_bubble['font'],
                            speech_bubble=speech_bubble['speech_bubble'],
                            writing_areas=speech_bubble['writing_areas'],
                            resize_to=speech_bubble['resize_to'],
                            location=speech_bubble['location'],
                            transforms=speech_bubble['transforms'],
                            text_orientation=speech_bubble['text_orientation']
                            )

                self.speech_bubbles.append(bubble)

        children = []
        if len(data['children']) > 0:
            for child in data['children']: 
                panel = Panel(
                    coords=child['coordinates'],
                    name=child['name'],
                    parent=self,
                    orientation=child['orientation'],
                    non_rect=child['non_rect']
                )

                panel.load_data(child)
                children.append(panel)

        self.children = children

class Page(Panel):

    def __init__(self, coords=[], page_type="", num_panels=None, children=[]):

        if len(coords) < 1:
            topleft = (0.0, 0.0)
            topright = (cfg.page_width, 0.0)
            bottomleft = (0.0, cfg.page_height)
            bottomright = cfg.page_size 
            coords = [
                topleft,
                topright,
                bottomright,
                bottomleft
            ]

        super().__init__(coords, "page", None, None, [])

        self.num_panels = num_panels
        self.page_type = page_type

        self.background = None
        self.leaf_children = []
        self.page_size = cfg.page_size

        # TODO: Setup naming of pages
        self.name = str(uuid.uuid1())

    def dump_data(self, dataset_path, dry=True):

        if len(self.children) > 0:
            children_rec = [child.dump_data() for child in self.children]
        else:
            children_rec = []

        data = dict(
            name = self.name,
            num_panels = int(self.num_panels),
            page_type = self.page_type,
            page_size = self.page_size,
            children = children_rec
        )   

        if not dry:
            with open(dataset_path+self.name+".json", "w+") as json_file:
                json.dump(data, json_file, indent=2)
        else:
            return json.dumps(data, indent=2)
    
    def load_data(self, filename):
        with open(filename, "rb") as json_file:
            data = json.load(json_file)
            self.name = data['name']
            self.num_panels = int(data['num_panels'])
            self.page_type = data['page_type']

            if len(data['children']) > 0:
                for child in data['children']: 
                    panel = Panel(
                        coords=child['coordinates'],
                        name=child['name'],
                        parent=self,
                        orientation=child['orientation'],
                        non_rect=child['non_rect']
                    )
                    panel.load_data(child)
                    self.children.append(panel)


    def render(self, show=False):

        leaf_children = []
        if len(self.leaf_children) < 1:
            get_leaf_panels(self, leaf_children)
        else:
            leaf_children = self.leaf_children


        W = cfg.page_width
        H = cfg.page_height

        page_img = Image.new(size=(W,H), mode="L", color="white")
        draw_rect = ImageDraw.Draw(page_img)

        if self.background is not None:
            bg = Image.open(self.background).convert("L")
            img_array = np.asarray(bg)
            crop_array = crop_image_only_outside(img_array)
            bg = Image.fromarray(crop_array)
            bg = bg.resize((W,H))
            page_img.paste(bg, (0, 0))

        coords = []

        # Render panels
        for panel in leaf_children:

            img = Image.open(panel.image)

            img_array = np.asarray(img)
            crop_array = crop_image_only_outside(img_array)

            img = Image.fromarray(crop_array)

            w_rev_ratio = cfg.page_width/img.size[0]
            h_rev_ratio = cfg.page_height/img.size[1]


            #TODO Figure out how to do different types of 
            # image crops for smaller panels

            img = img.resize(
                (round(img.size[0]*w_rev_ratio),
                round(img.size[1]*h_rev_ratio))
            )

            mask = Image.new("L", cfg.page_size, 0)
            draw_mask = ImageDraw.Draw(mask)

            rect = panel.get_polygon()

            draw_mask.polygon(rect, fill=255)
            draw_rect.line(rect, fill="black", width=10) 

            page_img.paste(img, (0, 0), mask)

        # Render bubbles
        for panel in leaf_children:
            # For each bubble
                # Do for bubble
            for sb in panel.speech_bubbles:
                states, bubble, mask, location = sb.render()
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
    def __init__(self, texts, texts_indices, font, speech_bubble, writing_areas, resize_to, location, transforms=None, text_orientation=None):

        self.texts = texts
        # Index of dataframe for the text
        self.texts_indices = texts_indices
        self.font = font
        self.speech_bubble = speech_bubble
        self.writing_areas = writing_areas
        self.resize_to = resize_to 

        # Location on panel
        self.location = location

        if transforms is None:
            possible_transforms = [
                "flip horizontal",
                "flip vertical",
                "rotate",
                "stretch_x",
                "stretch y",
                ]
            # 1 in 50 chance of no transformation
            if np.random.rand() < 0.98:
                self.transforms = list(np.random.choice(possible_transforms, 2))

                # 1 in 20 chance of inversion
                if np.random.rand() < 0.05:
                    self.transforms.append("invert")
            else:
                self.transforms = []
        else:
            self.transforms = transforms
        
        if text_orientation is None:
            # 1 in 100 chance
            if np.random.random() < 0.01:
                self.text_orientation = "ltr"
            else:
                self.text_orientation = "ttb"
        else:
            self.text_orientation = text_orientation

    def dump_data(self):

        data = dict(
            texts = self.texts,
            texts_indices = self.texts_indices,
            font = self.font,
            speech_bubble = self.speech_bubble,
            writing_areas = self.writing_areas,
            resize_to = self.resize_to,
            location = self.location,
            transforms = self.transforms,
            text_orientation = self.text_orientation
        )

        return data

    def render(self):

        bubble = Image.open(self.speech_bubble).convert("L")
        mask = bubble.copy()


        # Set variable font size
        min_font_size = 54
        max_font_size = 72
        current_font_size = np.random.randint(min_font_size,
                                              max_font_size
                                              )
        # TODO: re-evaluate fonts
        font = ImageFont.truetype(self.font,current_font_size)

        w, h = bubble.size
        cx, cy = w/2, h/2

        states = []
        # Pre-render transforms
        for transform in self.transforms:
            if transform == "invert":
                states.append("inverted")
                bubble = ImageOps.invert(bubble)
            
            elif transform == "flip vertical": 
                bubble = ImageOps.flip(bubble)
                mask = ImageOps.flip(mask)
                # TODO: vertically flip box coordinates
                new_writing_areas = []
                for area in self.writing_areas:
                    og_height = area['original_height']

                    # Convert from percentage to actual values
                    px_height =  (area['height']/100)*og_height

                    og_y = ((area['y']/100)*og_height)
                    cydist = abs(cy - og_y)
                    new_y = (2*cydist + og_y) - px_height
                    new_y = (new_y/og_height)*100
                    area['y'] = new_y
                    new_writing_areas.append(area)

                self.writing_areas = new_writing_areas
                states.append("vflip")

            elif transform == "flip horizontal":
                bubble = ImageOps.mirror(bubble)
                mask = ImageOps.mirror(mask)
                # TODO: horizontally flip box coordinates
                new_writing_areas = []
                for area in self.writing_areas:
                    og_width = area['original_width']

                    # Convert from percentage to actual values
                    px_width =  (area['width']/100)*og_width

                    og_x = ((area['x']/100)*og_width)
                    # og_y = ((area['y']/100)*og_height)
                    cxdist = abs(cx - og_x)
                    new_x = (2*cxdist + og_x) - px_width
                    new_x = (new_x/og_width)*100
                    area['x'] = new_x
                    new_writing_areas.append(area)

                self.writing_areas = new_writing_areas
                states.append("hflip")
            
            elif transform == "stretch x":
                # Up to 30% stretching
                stretch_factor = np.random.random()*0.3
                new_size = (round(w*(1+stretch_factor)),h)

                # Reassign for resizing later
                w, h = new_size
                bubble = bubble.resize(new_size)
                mask = mask.resize(new_size)

                new_writing_areas = []
                for area in self.writing_areas:
                    og_width = area['original_width']

                    # Convert from percentage to actual values
                    px_width =  (area['width']/100)*og_width

                    area['original_width'] = og_width*(1+stretch_factor)
                
                    new_writing_areas.append(area)

                self.writing_areas = new_writing_areas
                states.append("xstretch")

            elif transform == "stretch y":
                stretch_factor = np.random.random()*0.3
                new_size = (w,round(h*(1+stretch_factor)))

                # Reassign for resizing later
                w, h = new_size
                bubble = bubble.resize(new_size)
                mask = mask.resize(new_size)

                new_writing_areas = []
                for area in self.writing_areas:
                    og_height = area['original_height']

                    # Convert from percentage to actual values
                    px_height =  (area['height']/100)*og_height
    
                    area['original_height'] = og_height*(1+stretch_factor)
                
                    new_writing_areas.append(area)

                self.writing_areas = new_writing_areas
                states.append("ystretch")

        # Write text into bubble
        write = ImageDraw.Draw(bubble)
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

            # at = (og_x, og_y, og_x+px_width, og_y+px_height)
            # write.rectangle(at, outline="black")

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
                            # language="ja",
                            fill=fill_type,
                            direction=self.text_orientation)

        # reisize bubble
        aspect_ratio = h/w
        new_height = round(np.sqrt(self.resize_to/aspect_ratio))
        new_width = round(new_height * aspect_ratio)
        bubble = bubble.resize((new_height, new_width))
        mask = mask.resize((new_height, new_width))

        # Make sure bubble doesn't bleed the page 
        x1, y1 = self.location
        x2 = x1 +bubble.size[0]
        y2 = y1 +bubble.size[1]

        if x2 > cfg.page_width:
            x1 = x1 - (x2-cfg.page_width)
        if y2 > cfg.page_height:
            y1 = y1 - (y2-cfg.page_height)
        
        self.location = (x1, y1)

        # perform rotation if it was in transforms
        if "rotate" in self.transforms:
            rotation = np.random.randint(10, 30)
            bubble = bubble.rotate(rotation)
            mask = mask.rotate(rotation)

        return states, bubble, mask, self.location

