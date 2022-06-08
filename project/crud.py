from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "somehash"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_image_by_id(db: Session, send_id: int):
    return db.query(models.Image).filter(models.Image.id == send_id).all()


def get_images(db: Session):
    return db.query(models.Image).all()


def create_image(db: Session, send_id: int, send_name: str, send_time: datetime):
    db_item = models.Image(id=send_id, name=send_name, time=send_time)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def del_images(db: Session, send_id: int):
    images = []
    time = 0
    image_list = db.query(models.Image).filter(models.Image.id == send_id)
    for i in image_list:
        images.append(i.name)
    if len(images) > 0:
        time = image_list[0].time
    db.query(models.Image).filter(models.Image.id == send_id).delete()
    db.commit()
    return images, time
