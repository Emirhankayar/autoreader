import os
from PIL import Image
from loader import load_image
from scan import scan_image
from read import read_image
from parse import parse_image


def main(directory):
    for filename in os.listdir(directory):
        image_path = os.path.join(directory, filename)
        image = load_image(image_path)
        if image is not None:
            processed_image = scan_image(image)
            if processed_image is not None:
                pil_image = Image.fromarray(processed_image)
                text = read_image(pil_image)
                print(text)
                parse_image(text)


if __name__ == "__main__":
    main("./images")
