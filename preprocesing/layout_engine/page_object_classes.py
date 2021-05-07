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
    """
    A class to encapsulate a panel of the manga page.
    Since the script works in a parent-child relationship
    where each panel child is an area subset of some parent panel,
    some panels aren't leaf nodes and thus not rendered.

    :param coords: Coordinates of the boundary of the panel

    :type coords: list

    :param name: Unique name for the panel

    :type name: str

    :param parent: The panel which this panel is a child of

    :type parent: Panel

    :param orientation: Whether the panel consists of lines that are vertically
    or horizotnally oriented in reference to the page

    :type orientation: str

    :children: Children panels of this panel

    :type children: list

    :non_rect: Whether the panel was transformed to be non rectangular
    and thus has less or more than 4 coords

    :type non_rect: bool, optional
    """

    def __init__(self,
                 coords,
                 name,
                 parent,
                 orientation,
                 children=[],
                 non_rect=False):
        """
        Constructor methods
        """

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

        area_proportion = round(self.area/(cfg.page_height*cfg.page_width), 2)
        self.area_proportion = area_proportion

        if len(children) > 0:
            self.children = children
        else:
            self.children = []

        self.orientation = orientation

        # Whether or not this panel has been transformed by slicing into two
        self.sliced = False

        # Whether or not to render this panel
        self.no_render = False

        # Image from the illustration dataset which is
        # the background of this panel
        self.image = None

        # A list of speech bubble objects to render around this panel
        self.speech_bubbles = []

    def get_polygon(self):
        """
        Return the coords in a format that can be used to render a polygon
        via Pillow

        :return: A tuple of coordinate tuples of the polygon's vertices
        :rtype: tuple
        """
        if self.non_rect:

            return tuple(self.coords)
        else:

            return (
                self.x1y1,
                self.x2y2,
                self.x3y3,
                self.x4y4,
                self.x1y1
            )

    def refresh_coords(self):
        """
        When chances are made to the xy coordinates variables directly
        this function allows you to refresh the coords variable with
        the changes
        """

        self.coords = [
            self.x1y1,
            self.x2y2,
            self.x3y3,
            self.x4y4,
            self.x1y1
        ]

    def refresh_vars(self):
        """
        When chances are made to the xy coordinates directly
        this function allows you to refresh the x1y1... variable with
        the changes
        """

        self.x1y1 = self.coords[0]
        self.x2y2 = self.coords[1]
        self.x3y3 = self.coords[2]
        self.x4y4 = self.coords[3]

    def add_child(self, panel):
        """
        Add child panels

        :param panel: A child panel to the current panel

        :type panel: Panel
        """
        self.children.append(panel)

    def add_children(self, panels):
        """
        Method to add multiple children at once

        :param panels: A list of Panel objects

        :type panels: list
        """

        for panel in panels:
            self.add_child(panel)

    def get_child(self, idx):
        """
        Get a child panel by index

        :param idx: Index of a child panel

        :type idx: int

        :return: The child at the idx
        :rtype: Panel
        """
        return self.children[idx]

    def dump_data(self):
        """
        A method to take all the Panel's relevant data
        and create a dictionary out of it so it can be
        exported to JSON via the Page(Panel) class's
        dump_data method

        :return: A dictionary of the Panel's data
        :rtype: dict
        """

        # Recursively dump children
        if len(self.children) > 0:
            children_rec = [child.dump_data() for child in self.children]
        else:
            children_rec = []

        speech_bubbles = [bubble.dump_data() for bubble in self.speech_bubbles]
        data = dict(
                name=self.name,
                coordinates=self.coords,
                orientation=self.orientation,
                children=children_rec,
                non_rect=self.non_rect,
                sliced=self.sliced,
                no_render=self.no_render,
                image=self.image,
                speech_bubbles=speech_bubbles
        )

        return data

    def load_data(self, data):
        """
        This method reverses the dump_data function and
        load's the metadata of the panel from the subsection
        of the JSON file that has been loaded

        :param data: A dictionary of this panel's data

        :type data: dict
        """

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
                            width=speech_bubble['width'],
                            height=speech_bubble['height'],
                            transforms=speech_bubble['transforms'],
                            text_orientation=speech_bubble['text_orientation']
                            )

                self.speech_bubbles.append(bubble)

        # Recursively load children
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
    """
    A class that represents a full page consiting of multiple child panels

    :param coords: A list of the boundary coordinates of a page

    :type coords: list

    :param page_type: Signifies whether a page consists of vertical
    or horizontal panels or both

    :type page_type: str

    :param num_panels: Number of panels in this page

    :type num_panels: int

    :param children: List of direct child panels of this page

    :type children: list, optional:
    """

    def __init__(self,
                 coords=[],
                 page_type="",
                 num_panels=1,
                 children=[],
                 name=None
                 ):
        """
        Constructor method
        """

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

        if name is None:
            self.name = str(uuid.uuid1())
        else:
            self.name = name

        # Initalize the panel super class
        super().__init__(coords=coords,
                         name=self.name,
                         parent=None,
                         orientation=None,
                         children=[]
                         )

        self.num_panels = num_panels
        self.page_type = page_type

        # Whether this page needs to be rendered with a background
        self.background = None

        # The leaf children of tree of panels
        # These are the panels that are actually rendered
        self.leaf_children = []

        # Size of the page
        self.page_size = cfg.page_size

    def dump_data(self, dataset_path, dry=True):
        """
        A method to take all the Page's relevant data
        and create a dictionary out of it so it can be
        exported to JSON so that it can then be loaded
        and rendered to images in parallel

        :param dataset_path: Where to dump the JSON file

        :type dataset_path: str

        :param dry: Whether to just return or write the JSON file

        :type dry: bool, optional

        :return: Optional return when running dry of a json data dump
        :rtype: str
        """

        # Recursively dump children
        if len(self.children) > 0:
            children_rec = [child.dump_data() for child in self.children]
        else:
            children_rec = []

        speech_bubbles = [bubble.dump_data() for bubble in self.speech_bubbles]
        data = dict(
            name=self.name,
            num_panels=int(self.num_panels),
            page_type=self.page_type,
            page_size=self.page_size,
            background=self.background,
            children=children_rec,
            speech_bubbles=speech_bubbles
        )

        if not dry:
            with open(dataset_path+self.name+".json", "w+") as json_file:
                json.dump(data, json_file, indent=2)
        else:
            return json.dumps(data, indent=2)

    def load_data(self, filename):

        """
        This method reverses the dump_data function and
        load's the metadata of the page from the JSON
        file that has been loaded.

        :param filename: JSON filename to load

        :type filename: str
        """
        with open(filename, "rb") as json_file:

            data = json.load(json_file)

            self.name = data['name']
            self.num_panels = int(data['num_panels'])
            self.page_type = data['page_type']
            self.background = data['background']

            if len(data['speech_bubbles']) > 0:
                for speech_bubble in data['speech_bubbles']:
                    # Line constraints
                    text_orientation = speech_bubble['text_orientation']
                    bubble = SpeechBubble(
                                texts=speech_bubble['texts'],
                                texts_indices=speech_bubble['texts_indices'],
                                font=speech_bubble['font'],
                                speech_bubble=speech_bubble['speech_bubble'],
                                writing_areas=speech_bubble['writing_areas'],
                                resize_to=speech_bubble['resize_to'],
                                location=speech_bubble['location'],
                                width=speech_bubble['width'],
                                height=speech_bubble['height'],
                                transforms=speech_bubble['transforms'],
                                text_orientation=text_orientation
                                )

                    self.speech_bubbles.append(bubble)

            # Recursively load children
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
        """
        A function to render this page to an image

        :param show: Whether to return this image or to show it

        :type show: bool, optional
        """

        leaf_children = []
        if self.num_panels > 1:
            # Get all the panels to be rendered
            if len(self.leaf_children) < 1:
                get_leaf_panels(self, leaf_children)
            else:
                leaf_children = self.leaf_children

        W = cfg.page_width
        H = cfg.page_height

        # Create a new blank image
        page_img = Image.new(size=(W, H), mode="L", color="white")
        draw_rect = ImageDraw.Draw(page_img)

        # Set background if needed
        if self.background is not None:
            bg = Image.open(self.background).convert("L")
            img_array = np.asarray(bg)
            crop_array = crop_image_only_outside(img_array)
            bg = Image.fromarray(crop_array)
            bg = bg.resize((W, H))
            page_img.paste(bg, (0, 0))

        # Render panels
        for panel in leaf_children:

            # Panel coords
            rect = panel.get_polygon()

            # Open the illustration to put within panel
            if panel.image is not None:
                img = Image.open(panel.image)

                # Clean it up by cropping the black areas
                img_array = np.asarray(img)
                crop_array = crop_image_only_outside(img_array)

                img = Image.fromarray(crop_array)

                # Resize it to the page's size as a simple
                # way to crop differnt parts of it

                # TODO: Figure out how to do different types of
                # image crops for smaller panels
                w_rev_ratio = cfg.page_width/img.size[0]
                h_rev_ratio = cfg.page_height/img.size[1]

                img = img.resize(
                    (round(img.size[0]*w_rev_ratio),
                     round(img.size[1]*h_rev_ratio))
                )

                # Create a mask for the panel illustration
                mask = Image.new("L", cfg.page_size, 0)
                draw_mask = ImageDraw.Draw(mask)

                # On the mask draw and therefore cut out the panel's
                # area so that the illustration can be fit into
                # the page itself
                draw_mask.polygon(rect, fill=255)

            # Draw outline
            draw_rect.line(rect, fill="black", width=cfg.boundary_width)

            # Paste illustration onto the page
            if panel.image is not None:
                page_img.paste(img, (0, 0), mask)

        # If it's a single panel page
        if self.num_panels < 2:
            leaf_children.append(self)

        # Render bubbles
        for panel in leaf_children:
            if len(panel.speech_bubbles) < 1:
                continue
            # For each bubble
            for sb in panel.speech_bubbles:
                states, bubble, mask, location = sb.render()
                # Slightly shift mask so that you get outline for bubbles
                new_mask_width = mask.size[0]+cfg.bubble_mask_x_increase
                new_mask_height = mask.size[1]+cfg.bubble_mask_y_increase
                bubble_mask = mask.resize((new_mask_width, new_mask_height))

                w, h = bubble.size
                crop_dims = (
                    5, 5,
                    5+w, 5+h,
                )
                # Uses a mask so that the "L" type bubble is cropped
                bubble_mask = bubble_mask.crop(crop_dims)
                page_img.paste(bubble, location, bubble_mask)

        if show:
            page_img.show()
        else:
            return page_img


class SpeechBubble(object):
    """
    A class to represent the metadata to render a speech bubble

    :param texts: A list of texts from the text corpus to render in this
    bubble

    :type texts: lists

    :param texts_indices: The indices of the text from the dataframe
    for easy retrival

    :type texts_indices: lists

    :param font: The path to the font used in the bubble

    :type font: str

    :param speech_bubble: The path to the base speech bubble file
    used for this bubble

    :type speech_bubble: str

    :param writing_areas: The areas within the bubble where it is okay
    to render text

    :type writing_areas: list

    :param resize_to: The amount of area this text bubble should consist of
    which is a ratio of the panel's area

    :type resize_to: float

    :param location: The location of the top left corner of the speech bubble
    on the page

    :type location: list

    :param width: Width of the speech bubble, defaults to 0

    :type width: float, optional

    :param height: Height of the speech bubble, defaults to 0

    :type height: float, optional

    :param transforms: A list of transformations to change
    the shape of the speech bubble

    :type transforms: list, optional

    :param text_orientation: Whether the text of this speech bubble
    is written left to right ot top to bottom

    :type text_orientation: str, optional
    """
    def __init__(self,
                 texts,
                 texts_indices,
                 font,
                 speech_bubble,
                 writing_areas,
                 resize_to,
                 location,
                 width=0,
                 height=0,
                 transforms=None,
                 text_orientation=None):
        """
        Constructor method
        """

        self.texts = texts
        # Index of dataframe for the text
        self.texts_indices = texts_indices
        self.font = font
        self.speech_bubble = speech_bubble
        self.writing_areas = writing_areas
        self.resize_to = resize_to

        # Location on panel
        self.location = location
        if width == 0:
            img = Image.open(speech_bubble)
            w, h = img.size
            self.width = w
            self.height = h
        else:
            self.width = width
            self.height = height

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
                self.transforms = list(np.random.choice(
                                            possible_transforms,
                                            2
                                            )
                                       )

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
        """
        A method to take all the SpeechBubble's relevant data
        and create a dictionary out of it so it can be
        exported to JSON via the Page(Panel) class's
        dump_data method

        :return: Data to be returned to Page(Panel) class's
        dump_data method
        :rtype: dict
        """
        data = dict(
            texts=self.texts,
            texts_indices=self.texts_indices,
            font=self.font,
            speech_bubble=self.speech_bubble,
            writing_areas=self.writing_areas,
            resize_to=self.resize_to,
            location=self.location,
            width=self.width,
            height=self.height,
            transforms=self.transforms,
            text_orientation=self.text_orientation
        )

        return data

    def render(self):
        """
        A function to render this speech bubble

        :return: A list of states of the speech bubble,
        the speech bubble itself, it's mask and it's location
        on the page
        :rtype: tuple
        """

        bubble = Image.open(self.speech_bubble).convert("L")
        mask = bubble.copy()

        # Set variable font size
        min_font_size = 54
        max_font_size = 72
        current_font_size = np.random.randint(min_font_size,
                                              max_font_size
                                              )
        font = ImageFont.truetype(self.font, current_font_size)

        # Center of bubble
        w, h = bubble.size
        cx, cy = w/2, h/2

        # States is used to indicate whether this bubble is
        # inverted or not to the page render function
        states = []

        # Pre-rendering transforms
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
                    px_height = (area['height']/100)*og_height

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
                new_writing_areas = []
                for area in self.writing_areas:
                    og_width = area['original_width']

                    # Convert from percentage to actual values
                    px_width = (area['width']/100)*og_width

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
                new_size = (round(w*(1+stretch_factor)), h)

                # Reassign for resizing later
                w, h = new_size
                bubble = bubble.resize(new_size)
                mask = mask.resize(new_size)

                new_writing_areas = []
                for area in self.writing_areas:
                    og_width = area['original_width']

                    # Convert from percentage to actual values
                    px_width = (area['width']/100)*og_width

                    area['original_width'] = og_width*(1+stretch_factor)

                    new_writing_areas.append(area)

                self.writing_areas = new_writing_areas
                states.append("xstretch")

            elif transform == "stretch y":
                stretch_factor = np.random.random()*0.3
                new_size = (w, round(h*(1+stretch_factor)))

                # Reassign for resizing later
                w, h = new_size
                bubble = bubble.resize(new_size)
                mask = mask.resize(new_size)

                new_writing_areas = []
                for area in self.writing_areas:
                    og_height = area['original_height']

                    # Convert from percentage to actual values
                    px_height = (area['height']/100)*og_height

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
            px_width = (area['width']/100)*og_width
            px_height = (area['height']/100)*og_height

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

                # Maximum chars in line
                max_chars = int((px_height//avg_height))
                if size[0] > px_height:
                    # Using specialized wrapping library
                    if max_chars > 1:
                        text_segments = cjkwrap.wrap(text, width=max_chars)

                text_max_w = len(text_segments)*size[1]

                is_fit = False

                # Horizontal wrapping
                # Reduce font or remove words till text fits
                while not is_fit:
                    if text_max_w > px_width:
                        if current_font_size > min_font_size:
                            current_font_size -= 1
                            font = ImageFont.truetype(self.font,
                                                      current_font_size)
                            size = font.getsize(text)
                            avg_height = size[0]/len(text)
                            max_chars = int((max_y//avg_height))
                            if max_chars > 1:
                                text_segments = cjkwrap.wrap(text,
                                                             width=max_chars)

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
                    if max_chars > 1:
                        text_segments = cjkwrap.wrap(text, width=max_chars)

                # Setup vertical wrapping
                text_max_h = len(text_segments)*size[1]
                is_fit = False
                while not is_fit:
                    if text_max_h > px_height:
                        if current_font_size > min_font_size:
                            current_font_size -= 1
                            font = ImageFont.truetype(self.font,
                                                      current_font_size)
                            size = font.getsize(text)
                            avg_width = size[0]/len(text)
                            max_chars = int((px_width//avg_width))
                            if max_chars > 1:
                                text_segments = cjkwrap.wrap(text,
                                                             width=max_chars)
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
                    rx = ((cbx + text_max_w/2) -
                          ((len(text_segments) - i)*size[1]))

                    ry = y
                else:
                    seg_size = font.getsize(text)
                    rx = cbx - seg_size[0]/2
                    ry = ((cby + (len(text_segments)*size[1])/2) -
                          ((len(text_segments) - i)*size[1]))

                write.text((rx, ry),
                           text,
                           font=font,
                           fill=fill_type,
                           direction=self.text_orientation)

        # reisize bubble
        aspect_ratio = h/w
        new_height = round(np.sqrt(self.resize_to/aspect_ratio))
        new_width = round(new_height * aspect_ratio)
        bubble = bubble.resize((new_width, new_height))
        mask = mask.resize((new_width, new_height))

        # Make sure bubble doesn't bleed the page
        x1, y1 = self.location
        x2 = x1 + bubble.size[0]
        y2 = y1 + bubble.size[1]

        if x2 > cfg.page_width:
            x1 = x1 - (x2-cfg.page_width)
        if y2 > cfg.page_height:
            y1 = y1 - (y2-cfg.page_height)

        self.location = (x1, y1)

        # perform rotation if it was in transforms
        # TODO: Fix issue of bad crops with rotation
        if "rotate" in self.transforms:
            rotation = np.random.randint(10, 30)
            bubble = bubble.rotate(rotation)
            mask = mask.rotate(rotation)

        return states, bubble, mask, self.location
