from PIL import Image



def create_single_page():

    # Default page size
    W = 1700
    H = 2400


    page = Image.new(size=(W,H), mode="L", color="white")
    page.show()