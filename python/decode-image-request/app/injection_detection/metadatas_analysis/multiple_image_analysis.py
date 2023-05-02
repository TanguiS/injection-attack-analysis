from typing import List

from app.images_decode.decoder import ExifLoader, TagName
from app.injection_detection.metadatas_analysis.single_image_analysis import *


def model_consistency(exif_list: List[ExifLoader]) -> bool:
    for i in range(0, len(exif_list) - 1):
        if exif_list[i] != exif_list[i + 1]:
            return False
    return True


def date_consistency(exif_list: List[ExifLoader]) -> bool:
    for exif in exif_list:
        if not single_date_consistency(convert_date_str(exif[TagName.DateTime.value])):
            return False
    total_time = 0
    for i in range(len(exif_list) - 1):
        total_time += abs(convert_date_str(exif_list[i][TagName.DateTime.value]) -
                          convert_date_str(exif_list[i + 1][TagName.DateTime.value]))
    return total_time / (len(exif_list) - 1) <= 1.0
