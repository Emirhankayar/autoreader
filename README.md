# Grocery Bills OCR

This project is specifically designed for Italian grocery shopping bills. It applies a variety of transformations to a given image and then performs image to document scan, OCR text extraction using pytesseract and parsing the words found. The accuracy of the readings may vary depending on the quality, exposure, etc., of the image file. It can read most image types, such as .HEIC, PNG, JPG, etc. 

Currently, program supports the scanning of images so it is implemented, a new update. However, please make sure image has a dark background, so the edge detection can return a legit result. (this will be taken care of in the future so you can use the image of the bill on any background). 

## FOR NOW ONLY TESTED WITH CONAD.

## Prerequisites

This project requires Python and Tesseract to be installed on your system.

### Python

You can download Python from the official website:

- [Download Python](https://www.python.org/downloads/)

### Tesseract

The installation process for Tesseract varies depending on your operating system.

#### Linux

You can install Tesseract using the package manager for your distribution. For example, on Ubuntu, you can use `apt`:

### Ubuntu

```bash
sudo apt update
sudo apt install tesseract-ocr
sudo apt install tesseract-ocr-eng
sudo apt install tesseract-ocr-ita
```

#### Fedora

```bash
sudo dnf upgrade --refresh
sudo dnf install tesseract 
sudo dnf install tesseract-langpack-eng
sudo dnf install tesseract-langpack-ita
```

#### Arch BTW
```bash
sudo pacman -Syu
sudo pacman -S tesseract
sudo pacman -S tesserect-data-eng
sudo pacman -S tesseract-data-it
```

#### macOS

You can install Tesseract using Homebrew:

```bash
brew install tesseract
```

#### Windows

You can download the Tesseract installer from the GitHub releases page:

- [Download Tesseract for Windows](https://github.com/UB-Mannheim/tesseract/wiki)

## Dependencies

After installing Python and Tesseract, you can install the following Python dependencies for this project:

```bash
fuzzywuzzy==0.18.0
packaging==23.2
pillow==10.2.0
pytesseract==0.3.10
Wand==0.6.13
```

## Installation 

Clone the repository:

```bash
git clone www.github.com/emirhankayar/autoreader
```

Navigate to the project directory:

```bash
cd ~/autoreader
```

Install the necessary dependencies:

```bash
pip install -r requirements.txt
```

# DISCLAIMER & USAGE
## For now just 'CONAD' bills are tested out, other grocery bills probably does not have the same pattern as CONAD you might have NULL results.
Now this project supports auto scanning the files! so you do not have to scan each image yourself anymore. (BE CAREFUL WITH IMAGE QUALITY!)
YOU CAN RUN IT WITH MULTI IMAGES.

Place your images into the `~/autoreader/images` directory. Then, you can run the program with the following command:

```bash
cd ~/autoreader && python3 main.py
```

The output will be a CSV file located in the `~/autoreader/output` directory.
