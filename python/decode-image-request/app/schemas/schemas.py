from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
import uuid


class UserBase(BaseModel):
    name: str


class User(UserBase):
    id: uuid.UUID
    organization_id: uuid.UUID

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    id: uuid.UUID
    organization_id: uuid.UUID


class PhotoCompareBase(BaseModel):
    photo_one: str
    photo_two: str
    score: float


class PhotoCompare(PhotoCompareBase):
    class Config:
        orm_mode = True


class PhotoCompareCreate(PhotoCompareBase):
    pass


class ReportBase(BaseModel):  # Request structure JSON
    location: str
    document_owner_full_name: str
    date_of_birth: date
    gender: str
    social_security_number: str
    id_number: str
    document_type: str
    document_nr: str
    country_of_issue: str
    valid_to_date: date
    note: str
    helpdesk_note: str
    assessment_of_document_owner: bool
    rfid_photo_comparison: bool
    rfid_chip_data_aa: bool
    rfid_chip_certificate_pa: bool
    control_mrz_code: bool
    photo_comparisons: Optional[list[PhotoCompareCreate]] = []


class ReportResponse(BaseModel):
    id: uuid.UUID


class ReportResponseList(BaseModel):
    reports: list[ReportResponse] = []


class Report(ReportBase):  # Used when getting all report info, with images
    id: uuid.UUID
    organization_id: uuid.UUID
    creator: User
    created_at: datetime
    pdf: str
    passport_photo: str
    photo_comparisons: Optional[list[PhotoCompare]] = []

    class Config:
        orm_mode = True


class ReportCreate(ReportBase):
    passport_photo: str


class OrganizationBase(BaseModel):
    id: uuid.UUID


class OrganizationCreate(OrganizationBase):
    pass


class ReportContent(BaseModel):
    receiver_email_address: str
    first_name: str
    last_name: str
    date_of_birth: str
    identity_document_portrait_photo: str
    live_portrait_photo: str
    biometric_comparison_decision: bool
    biometric_pad_decision: bool
    chip_passive_authentication_success: bool
    chip_active_authentication_success: bool


class ImageList(BaseModel):
    image_list: list[str] = []


class ImageToDecode(BaseModel):
    str64_image: str


class ListOfImageToDecode(BaseModel):
    listStr64_image: list[str] = []
