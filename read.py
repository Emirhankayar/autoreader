import os
import io
import pytesseract
from multiprocessing import Pool
from wand.image import Image as WandImage
from PIL import Image as PI, ImageFilter, ImageOps

# TESERRACT CONFIG
# IF YOU ARE A WINDOWS USER GOOD LUCK SETTING THIS PART UP

os.environ["TESSDATA_PREFIX"] = "/usr/share/tesseract/tessdata/"

pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"
tessdata_dir_config = (
    r'--tessdata-dir "/usr/share/tesseract/tessdata" --oem 1 --psm 6 -l ita+eng'
)

#  LOAD


def read_image(image_path):
    print("LOADING...\n")
    if image_path.lower().endswith(".heic"):
        with WandImage(filename=image_path) as img:
            png_image_bytes = img.make_blob("PNG")
            png_image = PI.open(io.BytesIO(png_image_bytes))
        return ImageOps.exif_transpose(png_image)
    else:
        return ImageOps.exif_transpose(PI.open(image_path))


#

# PREPROCESS


def get_grayscale(image):
    print("GRAYSCALE...\n")
    return image.convert("L")


def remove_noise(image):
    print("REMOVING NOISE...\n")
    return image.filter(ImageFilter.MedianFilter(3))


def thresholding(image):
    print("THRESHOLDING...\n")
    return image.point(lambda x: 0 if x < 120 else 210, "1")


def dilate(image):
    print("DILATING...\n")
    return image.filter(ImageFilter.MinFilter(1))


def erode(image):
    print("ERODING...\n")
    return image.filter(ImageFilter.MaxFilter(1))


def opening(image):
    print("DILATING AND ERODING...\n")
    return dilate(erode(image))


def process_image(pil_image):
    print("PROCESSING...\n")
    image = pil_image.copy()

    image = get_grayscale(image)
    image = remove_noise(image)
    # image = thresholding(image)
    # image = erode(image)
    image = opening(image)

    # image.save('processed_image.png')

    return image


#

# EXTRACT TEXT


def extract_text(image):
    print("EXTRACTING TEXT...\n")
    whitelist = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ.,/:"
    config_options = tessdata_dir_config + f" -c tessedit_char_whitelist={whitelist}"
    return pytesseract.image_to_string(image, config=config_options)


def post_process(text):
    whitelist = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ.,/:"
    return "".join(c for c in text if c in whitelist or c.isspace())


def process_image_file(filename):
    directory = "./images"  # replace with your directory
    if filename.endswith(
        (".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif", ".heic", ".HEIC")
    ):
        image_path = os.path.join(directory, filename)
        image = read_image(image_path)
        processed_image = process_image(image)
        text = extract_text(processed_image)
        return text


def read_and_extract_text(directory):
    with Pool() as pool:
        filenames = os.listdir(directory)
        texts = pool.map(process_image_file, filenames)
    return texts


#
