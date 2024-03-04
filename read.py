import os
import pytesseract
import concurrent.futures
from PIL import ImageFilter


# TESERRACT CONFIG
# IF YOU ARE A WINDOWS USER GOOD LUCK SETTING THIS PART UP

os.environ["TESSDATA_PREFIX"] = "/usr/share/tesseract/tessdata/"

pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"
tessdata_dir_config = (
    r'--tessdata-dir "/usr/share/tesseract/tessdata" --oem 1 --psm 6 -l ita+eng'
)

# PREPROCESS FOR OCR


def get_grayscale(image):
    # print("GRAYSCALE...\n")
    return image.convert("L")


"""def remove_noise(image):
    print("REMOVING NOISE...\n")
    return image.filter(ImageFilter.MedianFilter(1))


def thresholding(image):
    print("THRESHOLDING...\n")
    return image.point(lambda x: 0 if x < 120 else 250, "1")
"""


def dilate(image):
    # print("DILATING...\n")
    return image.filter(ImageFilter.MinFilter(3))


def erode(image):
    # print("ERODING...\n")
    return image.filter(ImageFilter.MaxFilter(1))


def opening(image):
    # print("DILATING AND ERODING...\n")
    return dilate(erode(image))


def process_image(pil_image):
    # print("PROCESSING...\n")
    image = pil_image.copy()

    image = get_grayscale(image)
    # image = remove_noise(image)
    # image = sharpen_image(image)
    # image = thresholding(image)
    # image = erode(image)
    # image = dilate(image)
    image = opening(image)

    # image.save("read.png")

    return image


#

# EXTRACT TEXT


def resize_to_dpi(image, dpi):
    # Calculate the factor to resize the image by
    factor = dpi / 96  # 96 is the standard DPI for web images
    new_size = (int(image.size[0] * factor), int(image.size[1] * factor))

    # Resize the image
    resized_image = image.resize(new_size)

    return resized_image


def feedback_loop(args):
    image, dpi = args
    try:
        resized_image = resize_to_dpi(image, dpi)
        # whitelist = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ.,/:"
        # config_options = (
        #    tessdata_dir_config + f" -c tessedit_char_whitelist={whitelist}"
        # )
        config_options = tessdata_dir_config
        data = pytesseract.image_to_data(
            resized_image,
            config=config_options,
            output_type=pytesseract.Output.DATAFRAME,
        )
        data = data[data.conf != -1]
        lines = (
            data.groupby(["page_num", "block_num", "par_num", "line_num"])["text"]
            .apply(lambda x: " ".join(x))
            .tolist()
        )
        confs = (
            data.groupby(["page_num", "block_num", "par_num", "line_num"])["conf"]
            .mean()
            .tolist()
        )
        return dpi, lines, confs
    except Exception as e:
        print(f"An error occurred at DPI {dpi}: {e}")
        return dpi, [], []


def extract_text(image):
    # print("EXTRACTING TEXT...\n")
    dpi_values = range(30, 301, 30)  # DPI values from 30 to 300
    best_lines = {}

    with concurrent.futures.ProcessPoolExecutor() as executor:
        for dpi in dpi_values:
            results = list(executor.map(feedback_loop, [(image, dpi)]))
            for dpi, lines, confs in results:
                for i, (line, conf) in enumerate(zip(lines, confs)):
                    if i not in best_lines or best_lines[i][1] < conf:
                        best_lines[i] = (line, conf)

    # Combine the best lines to form the best text
    best_text = "\n".join(line for line, _ in best_lines.values())

    # #print out each line with its confidence
    # for i, (line, conf) in best_lines.items():
    # print(f"Line {i+1}: {line} (confidence: {conf}%)")

    return best_text


def read_image(image):
    processed_image = process_image(image)
    text = extract_text(processed_image)
    # processed_image.show()
    return text


#
