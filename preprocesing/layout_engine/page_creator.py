from PIL import Image, ImageDraw



def create_single_page():

    # Default page size
    W = 1700
    H = 2400


    page = Image.new(size=(W,H), mode="L", color="white")
    page.show()


def get_leaf_panels(page, coords=[]):

    for child in page.children:
        
        if len(child.children) > 0:
            get_leaf_panels(child, coords)
        else:
            coords.append(child)

def test_render(page):

    leaf_children = []
    get_leaf_panels(page, leaf_children)

    coords = []
    for panel in leaf_children:
        coords.append(panel.get_polygon())
    W = 1700
    H = 2400

    print(coords)
    page = Image.new(size=(W,H), mode="L", color="white")
    draw_rect = ImageDraw.Draw(page)

    for rect in coords:
        # draw_rect.rectangle(rect, fill=None, outline="white", width=20)
        draw_rect.line(rect, fill="black", width=20)
        # draw_rect.polygon(rect, fill="red", outline="yellow")

    page.show()