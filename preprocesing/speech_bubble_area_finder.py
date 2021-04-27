from PIL import Image, ImageFilter, ImageDraw
import os
from tqdm import tqdm
import numpy as np
import math
import pyclipper

# def check_fit(coords, )

def find_rect(min_points, max_points):

    # Initial proposal
    x1y1 = min_points[0]
    x2y2 = min_points[-1]
    x3y3 = max_points[0]
    x4y4 = max_points[-1]

    lowest_x = math.inf
    for point in min_points:
        if point[0] < lowest_x:
            lowest_x = point[0]

    higest_x = 0
    for point in max_points:
        if point[0] > higest_x:
            higest_x = point[0]

    width = higest_x - lowest_x
    height = x3y3[1] - x1y1[1]


    cx, cy = width/2, height/2
    print(width, height)

    x1y1 = (cx - width/4, cy - height/4)
    x3y3 = (cx + width/4, cy + height/4)

    coords = (
        x1y1,
        x2y2,
        x3y3,
        x4y4,
        x1y1
    )
    new_coords = (coords[0], coords[2])
    print(new_coords)
    fit = False
    # while not fit:
    # fit = check_fit(x1y1, x2y2, x3y3, x4y4)
    return new_coords

# Create a maximum proposal of a rectangle - 1 function (l, r)
# Check if it fits inside completely
    # If it does great
    # If not create another proposal which is smaller

def create_speech_bubble_metadata():
    speech_bubble_dataset_path = "datasets/speech_bubbles_dataset/files/"
    speech_bubbles = os.listdir(speech_bubble_dataset_path)
    speech_bubbles = speech_bubbles[0:1]

    for filename in tqdm(speech_bubbles):
        print(filename)
        img_type = filename.split("~")[0]
        bubble_img = Image.open(speech_bubble_dataset_path+filename)

        img = Image.new('RGB', bubble_img.size, (128, 128, 128)) 
        img.paste(bubble_img,(0, 0), mask=bubble_img)
        img = img.convert("L")
        img_array = np.asarray(img)

        # if white then find max white area
        # if black then find max black area
        if img_type == "black":
            bubble_area = np.argwhere(img_array == 0)
        else:
            bubble_area = np.argwhere(img_array == 255)

        y_values = np.unique(bubble_area[:,0])

        min_points = []
        max_points = []
        for i in range(0, len(y_values), 10):
            y = y_values[i]
            x_values = bubble_area[bubble_area[:, 0] == y][:, 1]
            min_x = np.min(x_values)
            max_x = np.max(x_values)
            min_points.append((min_x, y))
            max_points.append((max_x, y))

        max_points.reverse()
        points = min_points + max_points

        print(len(points))
        rect = find_rect(min_points, max_points)
        print(rect)
        draw = ImageDraw.Draw(img)
        draw.polygon(points, outline="white", fill=None)
        draw.rectangle(rect, fill="yellow")

        img.show()

