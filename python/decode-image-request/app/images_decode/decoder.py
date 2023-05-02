import base64
from enum import Enum
from typing import Any, Iterator, Tuple, List

from PIL import Image, ExifTags
from io import BytesIO

from app.schemas import schemas


class TagName(Enum):
    ImageWidth = "ImageWidth"
    ImageLength = "ImageLength"
    Model = "Model"
    Make = "Make"
    DateTime = "DateTime"


class ExifLoader:

    def __init__(self, base64_image: str) -> None:
        super().__init__()
        self._map = dict()
        for tag_name, tag_value in decode(base64_image):
            self._map[tag_name] = tag_value

    def __getitem__(self, item: str) -> str:
        return self._map[item]

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, ExifLoader):
            return False
        for tag in TagName.Make, TagName.Model, TagName.ImageWidth, TagName.ImageLength:
            if self._map[tag.value] != o[tag.value]:
                return False
        return True

    def __str__(self) -> str:
        out = "ExifStr from image:\n"
        for key in TagName:
            out += f"    {key.value}: {self._map[key.value]}\n"
        return out[:-1]


def decode(report) -> Iterator[Tuple[str, str]]:
    decoded_report = base64.b64decode(report)
    img = Image.open(BytesIO(decoded_report))
    metadata = img.getexif()
    for tag_id in metadata:
        tag_name = ExifTags.TAGS.get(tag_id, tag_id)
        tag_value = metadata.get(tag_id)
        yield tag_name, tag_value


def decode_list_of_image(rep: schemas.ListOfImageToDecode) -> List[ExifLoader]:
    exif_list = []
    try:
        for image_to_decode in rep.listStr64_image:
            exif_list.append(ExifLoader(image_to_decode))
    except:
        raise Exception("err")
    return exif_list
