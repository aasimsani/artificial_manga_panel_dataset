from PIL import Image, ImageDraw



def create_single_page():

    # Default page size
    W = 1700
    H = 2400


    page = Image.new(size=(W,H), mode="L", color="white")
    page.show()


def test_render(dims):

    W = 1700
    H = 2400
    print(dims)
    page = Image.new(size=(W,H), mode="L", color="white")
    draw_rect = ImageDraw.Draw(page)

    for rect in dims:
        # draw_rect.rectangle(rect, fill=None, outline="white", width=20)
        draw_rect.line(rect, fill="black", width=20)
        # draw_rect.polygon(rect, fill="red", outline="yellow")

    page.show()