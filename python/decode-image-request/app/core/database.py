from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi_utils.guid_type import setup_guids_postgresql
from .config import settings

if not settings.no_postgres:
    engine = create_engine(settings.get_db_url())
    setup_guids_postgresql(engine)

    # Each instance of this will be a session to the database
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Used to create database models
    Base = declarative_base()
else:
    SessionLocal = sessionmaker()
    Base = declarative_base()
