# downloader.py

import requests
from PIL import Image
from io import BytesIO

def download_and_resize_image(url, size=(1000, 1000)):
    print("downloading and resizing image...")
    response = requests.get(url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        image = image.resize(size, Image.LANCZOS)
        return image
    else:
        raise Exception(f"Failed to download image from {url}")

def download_file(url, local_path):
    print("downloading video...")
    response = requests.get(url)
    if response.status_code == 200:
        with open(local_path, 'wb') as f:
            f.write(response.content)
    else:
        raise Exception(f"Failed to download file from {url}")
