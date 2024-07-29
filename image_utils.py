from PIL import Image, ImageTk
import os
import logging
import matplotlib.pyplot as plt
from io import BytesIO

def display_image(image_path, image_label):
    '''Display the associated image if available.'''
    if image_path and os.path.exists(image_path):
        try:
            img = Image.open(image_path)
            img = img.resize((400, 300), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)
            image_label.config(image=img, text='')
            image_label.image = img
        except Exception as e:
            image_label.config(image='', text="Image not available.")
            logging.error(f"Error loading image {image_path}: {e}")
            logging.error("Exception occurred", exc_info=True)
    else:
        image_label.config(image='', text="No image available.")
        logging.warning(f"Image file not found: {image_path}")

def display_chart(data, title, image_label):
    '''Display a chart based on the provided data.'''
    try:
        fig, ax = plt.subplots()
        ax.bar(data.keys(), data.values())
        ax.set_title(title)
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img = Image.open(buf)
        img = img.resize((400, 300), Image.LANCZOS)
        img = ImageTk.PhotoImage(img)
        image_label.config(image=img, text='')
        image_label.image = img
    except Exception as e:
        image_label.config(image='', text="Chart not available.")
        logging.error(f"Error generating chart: {e}")
        logging.error("Exception occurred", exc_info=True)

def handle_image_error(image_label, error_message="Image not available"):
    '''Handle errors in image processing and display a message.'''
    image_label.config(image='', text=error_message)
    logging.error(error_message)
