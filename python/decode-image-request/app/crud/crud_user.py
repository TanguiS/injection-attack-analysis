from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas
import uuid


def create_user(db: Session, user: schemas.UserCreate):
    temp = get_user(db, user['id'])
    
    if temp == None:
        db_user = models.User(**user)
        db.add(db_user)
        db.commit()

        return db_user

    return temp


def get_user(db: Session, id: uuid.UUID):
    return db.query(models.User).filter(models.User.id == id).first()


def create_organization(db: Session, org: schemas.OrganizationCreate):
    temp = get_organization(db, org)
    
    if temp == None:
        db_org = models.Organization(id=org)
        db.add(db_org)
        db.commit()

        return db_org

    return temp


def get_organization(db: Session, id: uuid.UUID):
    return db.query(models.Organization).filter(models.Organization.id == id).first()
