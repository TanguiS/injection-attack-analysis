import base64
from PIL import Image, ExifTags
from io import BytesIO

from app.schemas import schemas


def decode_image(rep: schemas.ImageToDecode):
    try:
        report = rep.str64_image
        decode(report)
    except:
        raise Exception("err")


def decode(report):
    decoded_report = base64.b64decode(report)
    img = Image.open(BytesIO(decoded_report))
    metadata = img.getexif()
    print("Decoding...")
    for tag_id in metadata:
        tag_name = ExifTags.TAGS.get(tag_id, tag_id)
        tag_value = metadata.get(tag_id)
        print(f"{tag_name}: {tag_value}")


def decode_list_of_image(rep: schemas.ListOfImageToDecode):
    try:
        for image_to_decode in rep.listStr64_image:
            decode(image_to_decode)
    except:
        raise Exception("err")


