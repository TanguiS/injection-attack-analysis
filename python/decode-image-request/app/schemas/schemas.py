from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
import uuid


class UserBase(BaseModel):
    name: str



class ImageList(BaseModel):
    image_list: list[str] = []


class ImageToDecode(BaseModel):
    str64_image: str


class ListOfImageToDecode(BaseModel):
    listStr64_image: list[str] = []
