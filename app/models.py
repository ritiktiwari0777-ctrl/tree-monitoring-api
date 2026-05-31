from sqlalchemy import Column, Integer, String, Float, Date
from .database import Base

class Tree(Base):
    __tablename__ = "trees"

    id = Column(Integer, primary_key=True, index=True)
    species_name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    planting_date = Column(Date)
    health_status = Column(String)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)