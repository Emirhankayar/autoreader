import numpy as np
import cv2
import imutils
from skimage.filters import threshold_local


# TODO ADD LINE SEGMENTATION THEN TREAT EACH LINE AS A SEPARATE IMAGE


# function to order points to proper rectangle
def order_points(pts):

    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


# function to transform image to four points
def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array(
        [
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1],
        ],
        dtype="float32",
    )
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    return warped


# to find the largest contours on the image
def findLargestCountours(cntList, cntWidths):
    newCntList = []
    newCntWidths = []

    first_largest_cnt_pos = cntWidths.index(max(cntWidths))

    newCntList.append(cntList[first_largest_cnt_pos])
    newCntWidths.append(cntWidths[first_largest_cnt_pos])

    cntList.pop(first_largest_cnt_pos)
    cntWidths.pop(first_largest_cnt_pos)

    seccond_largest_cnt_pos = cntWidths.index(max(cntWidths))

    newCntList.append(cntList[seccond_largest_cnt_pos])
    newCntWidths.append(cntWidths[seccond_largest_cnt_pos])

    cntList.pop(seccond_largest_cnt_pos)
    cntWidths.pop(seccond_largest_cnt_pos)

    return newCntList, newCntWidths


def get_image(image, height=500):
    image = np.array(image)
    ratio = image.shape[0] / height
    orig = image.copy()
    image = imutils.resize(image, height=height)
    return image, orig, ratio


def process_image(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.bilateralFilter(image, 11, 17, 17)
    image = cv2.medianBlur(image, 5)
    edged = cv2.Canny(image, 30, 400)
    return edged


def get_contours(edged):
    countours, _ = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    cnts = sorted(countours, key=cv2.contourArea, reverse=True)
    return cnts


def filter_contours(cnts):
    screenCntList = []
    scrWidths = []
    for cnt in cnts:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        if len(approx) == 4:
            (X, Y, W, H) = cv2.boundingRect(cnt)
            screenCntList.append(approx)
            scrWidths.append(W)
    return screenCntList, scrWidths


def get_warp_threshold(orig, screenCnt, ratio):
    warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
    warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    T = threshold_local(warped, 11, offset=10, method="gaussian")
    warped = (warped > T).astype("uint8") * 255
    return warped


def scan_image(image_path):
    print("SCANNING...\n")
    image, orig, ratio = get_image(image_path)
    image = process_image(image)
    cnts = get_contours(image)
    screenCntList, scrWidths = filter_contours(cnts)
    screenCntList, scrWidths = findLargestCountours(screenCntList, scrWidths)

    if not len(screenCntList) >= 2:
        print("No rectangle found")
        return None
    elif scrWidths[0] != scrWidths[1]:
        print("Mismatch in rectangle")
        return None

    image = get_warp_threshold(orig, screenCntList[0], ratio)

    #    cv2.imwrite("scan.png", image)
    return image
