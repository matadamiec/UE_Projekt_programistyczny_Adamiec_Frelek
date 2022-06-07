import numpy as np
import pytesseract
import cv2
import os
import tempfile
import requests
from PIL.Image import Resampling
from PIL import Image


# get grayscale image
def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# noise removal
def remove_noise(image):
    return cv2.medianBlur(image, 1)


# thresholding
def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


# erosion
def erode(image):
    kernel = np.ones((2, 2), np.uint8)
    return cv2.erode(image, kernel, iterations=1)


def set_image_dpi(file_path):
    im = Image.open(file_path)
    im_resized = im.resize((768, 1024), Resampling.LANCZOS)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    temp_filename = temp_file.name
    im_resized.save(temp_filename, dpi=(300, 300))
    return temp_filename


def scan_vehicle_card(scan_url: str):
    file_name = tempfile.NamedTemporaryFile(suffix=".png", delete=False)

    res = requests.get(scan_url, stream=True)
    vehicle_card = open("tmp_vehcile_card.jpeg", "wb")
    vehicle_card.write(res.content)
    vehicle_card.close()

    image_to_ocr = cv2.imread(set_image_dpi(vehicle_card.name))
    os.remove(vehicle_card.name)
    vin_part = image_to_ocr[800:870, 100:550]
    desc_part = image_to_ocr[600:800, 100:550]

    vin_part = get_grayscale(vin_part)
    vin_part = remove_noise(vin_part)
    vin_part = thresholding(vin_part)
    # vin_part_gray = erode(vin_part)

    desc_part = get_grayscale(desc_part)
    desc_part = remove_noise(desc_part)
    desc_part = thresholding(desc_part)

    vin_filename = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    cv2.imwrite(vin_filename.name, vin_part)
    vin = None
    vin = pytesseract.image_to_string(Image.open(vin_filename.name),
                                      config='--psm 13 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNPERSTUVWXYZ0123456789')
    vin = vin.replace("\n", " ")

    desc_filename = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    cv2.imwrite(desc_filename.name, desc_part)
    vehicle_desc = None
    vehicle_desc = pytesseract.image_to_string(Image.open(desc_filename.name), config='--psm 3 --oem 3')
    vehicle_desc = vehicle_desc.replace("\n", " ")

    # print("vin: " + vin)
    # print("desc: " + vehicle_desc.lstrip())
    # cv2.imshow("Image", image_to_ocr)
    # cv2.imshow("vin_part", vin_part)
    # cv2.imshow("vehicle_desc", desc_part)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    if vin or vehicle_desc:
        return {"vin": vin, "description": vehicle_desc}
    else:
        return None
