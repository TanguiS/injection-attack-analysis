import base64
import sys
from typing import List

import cv2
import numpy as np

from app.images_decode.decoder import ExifLoader, TagName
from app.injection_detection.metadatas_analysis.single_image_analysis import *


def model_consistency(exif_list: List[ExifLoader]) -> bool:
    try:
        for i in range(0, len(exif_list) - 1):
            if exif_list[i] != exif_list[i + 1]:
                return False
        return True
    except KeyError:
        return False


def date_consistency(exif_list: List[ExifLoader]) -> bool:
    try:
        for exif in exif_list:
            if not single_date_consistency(convert_date_str(exif[TagName.DateTime.value])):
                return False
        total_time = 0
        for i in range(len(exif_list) - 1):
            total_time += abs(convert_date_str(exif_list[i][TagName.DateTime.value]) -
                              convert_date_str(exif_list[i + 1][TagName.DateTime.value]))
        return total_time / (len(exif_list) - 1) <= 1.0
    except KeyError:
        return False


def replay_detection(img64_list: List[str], save: bool = False) -> bool:
    cv2_load = []
    count = 0
    for img64 in img64_list:
        decoded_img = base64.b64decode(img64)
        tmp = cv2.imdecode(np.frombuffer(decoded_img, np.uint8), cv2.IMREAD_COLOR)
        tmp2 = cv2.cvtColor(tmp, cv2.COLOR_BGR2GRAY)
        cv2_load.append(tmp2)
        if save:
            cv2.imwrite(f"/media/img_injection_attack_analysis_gray_init{count}.jpg", tmp2)
        count += 1
    current = cv2_load.pop()
    mse_avg = 0
    counter = 0
    while len(cv2_load) != 0:
        for cv2_next in cv2_load:
            mse, diff = mean_square_error(current, cv2_next)
            mse_avg += mse
            counter += 1
            if save:
                cv2.imwrite(f"/media/img_injection_attack_analysis_diff{count}.jpg", diff)
            count += 1
            print("Image matching Error between the two images:", mse)
            if mse <= sys.float_info.epsilon:
                return False
        current = cv2_load.pop()
    mse_avg = mse_avg / counter
    print("Image matching avg Error between all images:", mse_avg)
    return True


def mean_square_error(img1, img2):
    h, w = img1.shape
    diff = cv2.subtract(img1, img2)
    err = np.sum(diff ** 2)
    compute_mse = err / (float(h * w))
    return compute_mse, diff
