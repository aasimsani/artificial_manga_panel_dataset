from PIL import Image, ImageDraw
import numpy as np

# from .page_dataset_creator import get_leaf_panels


def create_single_page():

    # Default page size
    W = 1700
    H = 2400


    page = Image.new(size=(W,H), mode="L", color="white")
    page.show()


def crop_image_only_outside(img,tol=0):
    # img is 2D image data
    # tol  is tolerance
    mask = img>tol
    m,n = img.shape
    mask0,mask1 = mask.any(0),mask.any(1)
    col_start,col_end = mask0.argmax(),n-mask0[::-1].argmax()
    row_start,row_end = mask1.argmax(),m-mask1[::-1].argmax()
    return img[row_start:row_end,col_start:col_end]


def render(page, show=False):

    leaf_children = []
    if len(page.leaf_children) < 1:
        # get_leaf_panels(page, leaf_children)
        page.get_lead_panels(leaf_children)
    else:
        leaf_children = page.leaf_children


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