import numpy as np 
import random
from PIL import Image, ImageDraw, ImageFont
import json
import uuid
from .helpers import crop_image_only_outside

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
        for panel in leaf_children:

            img = Image.open(panel.image)

            img_array = np.asarray(img)
            crop_array = crop_image_only_outside(img_array)

            img = Image.fromarray(crop_array)

            w_rev_ratio = 1700/img.size[0]
            h_rev_ratio = 2400/img.size[1]


            img = img.resize(
                (round(img.size[0]*w_rev_ratio),
                round(img.size[1]*h_rev_ratio))
            )

            #TODO Figure out how to do different types of 
            # image crops for smaller panels
            mask = Image.new("L", (1700, 2400), 0)
            draw_mask = ImageDraw.Draw(mask)

            rect = panel.get_polygon()

            draw_mask.polygon(rect, fill=255)
            draw_rect.line(rect, fill="black", width=10) 

            page_img.paste(img, (0, 0), mask)

        if show:
            page_img.show()
        else:
            return page_img
    
class SpeechBubble(object):
    def __init__(self, text, font, speech_bubble):

        self.text = text['Japanese']
        self.font = font
        self.speech_bubble = speech_bubble
        
        color_type = speech_bubble.split("/")
        color_type = color_type[-1].split("~")
        if color_type == "black":
            self.write_type = "white"
        else:
            self.write_type = "black"
        
        self.transform = None
        self.location = []

        # Can be  
        self.text_orientation = ""
    
    def render(self):

        bubble = Image.open(self.speech_bubble)

        cx, cy = bubble.size[0]/2, bubble.size[1]/2

        x = cx - (cx/2)
        y = cy - (cy/2)

        write = ImageDraw.Draw(bubble)
        font = ImageFont.truetype(self.font, 54)

        # Figure out line breakpoints
            # horizontal
            # vertical
        # Figure out where to start writing
            # From dataframe
        # Figure out text orientation (95/5 split)
            # Top to bottom - Right to Left
            # Left to right - Top to bottom

        write.multiline_text((x, y),
                    self.text,
                    font=font,
                    fill=self.write_type,

                    )
        bubble.show()
