from typing import List, Union

from pydantic import BaseModel
from datetime import datetime

class ItemBase(BaseModel):
    title: str
    description: Union[str, None] = None


class ImageCreate(ItemBase):
    pass


class Image(ItemBase):
    id: int
    name: str
    time: datetime
    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True