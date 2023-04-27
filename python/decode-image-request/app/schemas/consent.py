from datetime import datetime
from optparse import Option
from typing import Optional
import uuid
from typing import Optional
from pydantic import BaseModel


class ConsentBase(BaseModel):
    text_version: str = ""
    binding_info: str = ""
    time_stamp: Optional[datetime]


class ConsentCreate(ConsentBase):
    pass


class Consent(ConsentBase):
    id: Optional[uuid.UUID]


class ConsentGroupBase(BaseModel):
    id: uuid.UUID


class ConsentGroupCreate(ConsentGroupBase):
    pass


class ConsentGroup(BaseModel):
    id: Optional[uuid.UUID]
    consents: list[Consent]


class ConsentTenantGroups(BaseModel):
    groups: "list[ConsentGroupBase]"
