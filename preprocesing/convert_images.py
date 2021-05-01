import os
from tqdm import tqdm
from PIL import Image
import concurrent.futures
import time

image_dataset_dir = "datasets/image_dataset/tagged-anime-illustrations/danbooru-images/danbooru-images/"
processed_image_dir  = "datasets/image_dataset/db_illustrations_bw/"



def convert_single_image(image_path):
    img = Image.open(image_path)
    bw_img = img.convert("L")
    filename = image_path.split("/")[-1]
    bw_img.save(processed_image_dir+filename, "JPEG")



def convert_images_to_bw():
    if not os.path.isdir(processed_image_dir):
        os.mkdir(processed_image_dir)

    print("Converting images to black and white")
    image_folders = os.listdir(image_dataset_dir)
    for folder in tqdm(image_folders):
        folder_path = image_dataset_dir+folder + "/"
        if os.path.isdir(folder_path):
            image_paths = [folder_path + image for image in os.listdir(folder_path) if image.endswith(".jpg")]

            # Since image processing is CPU and IO intensive
            with concurrent.futures.ProcessPoolExecutor() as executor:
                results = list(tqdm(executor.map(convert_single_image, image_paths), total=len(image_paths)))

