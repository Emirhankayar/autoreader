from PIL import ImageOps, Image as PI
from wand.image import Image as WandImage
import io
import numpy as np


def load_image(image_path):
    # print("LOADING...\n")
    if image_path.lower().endswith(".heic"):
        with WandImage(filename=image_path) as img:
            png_image_bytes = img.make_blob("PNG")
            png_image = PI.open(io.BytesIO(png_image_bytes))
        image = ImageOps.exif_transpose(png_image)
    else:
        image = ImageOps.exif_transpose(PI.open(image_path))

    return np.array(image)
