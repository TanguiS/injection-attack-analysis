import base64
import glob
from PIL import Image, ImageOps,   JpegImagePlugin, ImageEnhance

image_list = []
for fname in glob.glob('./test_images/*.*'):
    with open(fname, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        image_list.append(encoded_string)
        
with open("file.txt", "w") as output:
    output.write(str(image_list))