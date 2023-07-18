import json
import random
import tkinter as tk
from io import BytesIO

import cv2
import numpy as np
import requests
from aifs_client.api.data_view_api import DataViewApi
from PIL import Image, ImageDraw, ImageTk
from pycocotools import mask as maskUtils
from pycocotools.coco import COCO

from data_client.utils.client import get_aifs_client

raw_data_view_id = ""
annotation_view_id = ""

aifs_client = get_aifs_client()
data_view_api = DataViewApi(aifs_client)

# Set the batch size
batch_size = 3

anno_type = 'mask'

def load_image_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        img_data = BytesIO(response.content)
        img = Image.open(img_data)
        return img
    else:
        print(f"Error: {response.status_code}")
        return None

def load_bbox_from_url(url):
    bbox_list = []
    response = requests.get(url)
    if response.status_code == 200:
        json_object = json.loads(response.content.decode('utf-8'))
        if "AnnoData" not in json_object:
            return bbox_list
        for data in json_object["AnnoData"]:
            bbox = data["Bbox"]
            bbox_list.append(bbox)
        return bbox_list
    else:
        print(f"Error: {response.status_code}")
        return None

def load_seg_from_url(url):
    seg_list = []
    response = requests.get(url)
    if response.status_code == 200:
        json_object = json.loads(response.content.decode('utf-8'))
        if "AnnoData" not in json_object:
            return seg_list
        for data in json_object["AnnoData"]:
            seg = data["Segmentation"]
            seg_list.append(seg)
        return seg_list
    else:
        print(f"Error: {response.status_code}")
        return None

def get_raw_data_id_list(raw_data_list):
    ans = []
    for raw_data in raw_data_list.raw_data_list:
        ans.append(raw_data["raw_data_id"])
    return ans

def draw_bbox(image, bbox_list, color=(255,0,0), width=2):
    draw = ImageDraw.Draw(image)
    for bbox in bbox_list:
        draw.rectangle([bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3]], outline=color, width=width)
    return image

def draw_masks(image, masks, alpha=128):
    masked_image = image.convert("RGBA")
    for data in masks:
        if type(data) == dict:
            # Handle compressed RLE format
            rle = data
        elif type(data) == list:
            # Handle polygon format
            rle = maskUtils.frPyObjects(data, image.size[1], image.size[0])
        else:
            raise Exception("invalid format")
            
        mask = maskUtils.decode(rle)
        mask = np.array(mask * alpha, dtype=np.uint8)
        mask_image = Image.fromarray(mask, mode='L')
        
        # Assign a random color to the mask
        color = tuple(np.random.randint(0, 256, size=3).tolist())
        
        mask_image_rgb = Image.new("RGBA", image.size, color + (0,))
        masked_image = Image.composite(mask_image_rgb, masked_image, mask_image)
    return masked_image

def draw_anno_on_image(image, anno_type, url):
    if anno_type == 'mask':
        seg_list = load_seg_from_url(url=url)
        if len(seg_list) == 0:
            return image
        
        return draw_masks(image=image, masks=seg_list)
    
    elif anno_type == 'bbox':
        bbox_list = load_bbox_from_url(url=url)
        return draw_bbox(image=image, bbox_list=bbox_list)
    else:
        raise Exception(f"invalid annotation type {anno_type}")
# Create a function to display the next batch of images
def display_images(start_idx):
    # Clear the existing images
    for label in image_labels:
        label.destroy()

    try:
        # Create an empty list to store the images in the batch
        batch_images = []
        print(f'start idx: {start_idx}, end idx: {start_idx+batch_size}')
        
        raw_data_list = data_view_api.get_raw_data_in_data_view(data_view_id = raw_data_view_id, offset=start_idx, limit=batch_size)
        anno_list = data_view_api.get_annotations_in_data_view(data_view_id = annotation_view_id, offset = 0, limit = batch_size, raw_data_id_list = get_raw_data_id_list(raw_data_list))
        anno_map = {}
        for anno_data in anno_list.annotation_list:
            raw_data_id = anno_data["raw_data_id"]
            anno_map[raw_data_id] = anno_data["url"]
        
        # Iterate over the files in the batch and open each image
        for raw_data in raw_data_list.raw_data_list:
            # Open the image
            img_url = raw_data["url"]
            raw_data_id = raw_data["raw_data_id"]
            print(f'show image: {raw_data_id}')
            img = load_image_from_url(img_url)
            
            img = draw_anno_on_image(image=img, anno_type=anno_type, url=anno_map[raw_data_id])
        
            # Resize the image to fit the window
            img = img.resize((300, 300), Image.Resampling.LANCZOS)

            # Convert the image to a Tkinter PhotoImage object
            photo = ImageTk.PhotoImage(img)

            # Add the PhotoImage object to the list of images in the batch
            batch_images.append(photo)
        print(f'batch images len: {len(batch_images)}')
        # Display the images in the batch
        for i, photo in enumerate(batch_images):
            label = tk.Label(window, image=photo)
            label.grid(row=0, column=i+1)
            
            label.image = photo
            # Store a reference to the label so we can destroy it later
            image_labels.append(label)
    except Exception as e:
        print(e)
    finally:
        # Update the start index
        start_idx += batch_size

        # Disable the "Next" button if there are no more images to display
        if len(batch_images) == 0:
            next_button.config(state=tk.DISABLED)

        # Enable the "Previous" button if we're not at the beginning
        if start_idx > batch_size:
            prev_button.config(state=tk.NORMAL)

        # Update the batch start index
        window.start_idx = start_idx

# Create the main window
window = tk.Tk()

# Set the window title
window.title("Image Viewer")

# Set the window size
window.geometry("1050x1050")

# Create a list to store the image labels
image_labels = []

# Create a "Next" button to display the next batch of images
next_button = tk.Button(window, text="Next", command=lambda: display_images(window.start_idx))
next_button.grid(row=1, column=2)

# Create a "Previous" button to display the previous batch of images
prev_button = tk.Button(window, text="Previous", command=lambda: display_images(window.start_idx - batch_size * 2))
prev_button.grid(row=1, column=0)
prev_button.config(state=tk.DISABLED)

# Display the first batch of images
display_images(0)

# Start the main event loop
window.mainloop()

