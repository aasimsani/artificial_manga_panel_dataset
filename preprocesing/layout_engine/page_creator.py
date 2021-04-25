from PIL import Image, ImageDraw

from .page_dataset_creator import get_leaf_panels


def create_single_page():

    # Default page size
    W = 1700
    H = 2400


    page = Image.new(size=(W,H), mode="L", color="white")
    page.show()




def test_render(page):

    leaf_children = []
    if len(page.leaf_children) < 1:
        get_leaf_panels(page, leaf_children)
    else:
        leaf_children = page.leaf_children


    W = 1700
    H = 2400

    page = Image.new(size=(W,H), mode="L", color="white")
    draw_rect = ImageDraw.Draw(page)

    coords = []
    for panel in leaf_children:

        img = Image.open(panel.image)
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

        page.paste(img, (0, 0), mask)



    # mask = Image.new("L", (1700, 2400), 0)

    # draw = ImageDraw.Draw(mask)

    # w_rev_ratio = 1700/img.size[0]
    # h_rev_ratio = 2400/img.size[1]

    # img = img.resize(
    #     (round(img.size[0]*w_rev_ratio),
    #     round(img.size[1]*h_rev_ratio))
    # )

    # mask_dims = panel.get_polygon()
    # draw.polygon(mask_dims, fill=255)

    # bc = Image.new("L", (1700, 2400))
    # bc.paste(img, (0, 0), mask)

    # bc.show()

    # coords = coords[0:2]
    # for rect in coords:
    #     # draw_rect.rectangle(rect, fill=None, outline="white", width=20)
    #     draw_rect.line(rect, fill="black", width=10)
    #     # draw_rect.polygon(rect, fill="red", outline="yellow")

    page.show()