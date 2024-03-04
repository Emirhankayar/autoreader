import os
import concurrent.futures
from PIL import Image
from loader import load_image
from scan import scan_image
from read import read_image
from parse import parse_image
from tqdm import tqdm


def main(directory):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for filename in tqdm(os.listdir(directory), desc="Processing images"):
            image_path = os.path.join(directory, filename)
            image = load_image(image_path)
            if image is not None:
                processed_image = scan_image(image)
                if processed_image is not None:
                    pil_image = Image.fromarray(processed_image)
                    future = executor.submit(read_image, pil_image)
                    text = future.result()
                    parse_image(text)


if __name__ == "__main__":
    main("./images")
