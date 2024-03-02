from read import read_and_extract_text
from parse import parse_text


def main(directory):
    for text in read_and_extract_text(directory):
        parse_text(text)


if __name__ == "__main__":
    main("./images")
