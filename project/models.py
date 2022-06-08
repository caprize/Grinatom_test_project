from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,DateTime
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    # images = relationship("Item", back_populates="owner")


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer,index=True)
    name = Column(String,primary_key=True, index=True)
    time= Column(DateTime, index=True)
    # owner_id = Column(Integer, ForeignKey("users.id"))
    #
    # owner = relationship("User", back_populates="items")