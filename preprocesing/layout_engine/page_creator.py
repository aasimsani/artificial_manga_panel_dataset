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
    get_leaf_panels(page, leaf_children)

    coords = []
    for panel in leaf_children:
        coords.append(panel.get_polygon())

    W = 1700
    H = 2400

    page = Image.new(size=(W,H), mode="L", color="white")
    draw_rect = ImageDraw.Draw(page)

    # coords = coords[0:2]
    for rect in coords:
        # draw_rect.rectangle(rect, fill=None, outline="white", width=20)
        draw_rect.line(rect, fill="black", width=10)
        # draw_rect.polygon(rect, fill="red", outline="yellow")

    page.show()