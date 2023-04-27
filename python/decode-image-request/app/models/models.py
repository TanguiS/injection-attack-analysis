from sqlalchemy import Boolean, Column, String, Date, TIMESTAMP, LargeBinary, ForeignKey, Float
from sqlalchemy.orm import relationship
from fastapi_utils.guid_type import GUID, GUID_SERVER_DEFAULT_POSTGRESQL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(GUID, primary_key=True, server_default=GUID_SERVER_DEFAULT_POSTGRESQL)
    organization_id = Column(GUID, ForeignKey("organizations.id"), nullable=False)
    created_by = Column(GUID, ForeignKey("users.id"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    pdf = Column(String)
    location = Column(String)
    comitted_by_full_name = Column(String)
    document_owner_full_name = Column(String)
    date_of_birth = Column(Date)
    gender = Column(String)
    social_security_number = Column(String)
    id_number = Column(String)
    document_type = Column(String)
    document_nr = Column(String)
    country_of_issue = Column(String)
    valid_to_date = Column(Date)
    note = Column(String)
    helpdesk_note = Column(String)
    assessment_of_document_owner = Column(Boolean)
    rfid_photo_comparison = Column(Boolean)
    rfid_chip_data_aa = Column(Boolean)
    rfid_chip_certificate_pa = Column(Boolean)
    control_mrz_code = Column(Boolean)
    passport_photo = Column(LargeBinary)

    photo_comparisons = relationship(
        "PhotoCompare", 
        back_populates="report"
    )

    organization = relationship(
        "Organization",
        back_populates="reports"
    )

    creator = relationship(
        "User", 
        back_populates="reports"
    )


class PhotoCompare(Base):
    __tablename__ = "photo_comparisons"

    id = Column(GUID, primary_key=True, server_default=GUID_SERVER_DEFAULT_POSTGRESQL)
    report_id = Column(GUID, ForeignKey("reports.id", ondelete="CASCADE"))
    photo_one = Column(LargeBinary)
    photo_two = Column(LargeBinary)
    score = Column(Float)

    report = relationship("Report", back_populates="photo_comparisons")


class User(Base):
    __tablename__ = "users"

    id = Column(GUID, primary_key=True)
    organization_id = Column(GUID, ForeignKey("organizations.id"), nullable=False)
    name = Column(String)

    organization = relationship("Organization", back_populates="users")
    reports = relationship("Report", back_populates="creator")


class Organization (Base):
    __tablename__ = "organizations"

    id = Column(GUID, primary_key=True)

    users = relationship("User", back_populates="organization")
    reports = relationship("Report", back_populates="organization")