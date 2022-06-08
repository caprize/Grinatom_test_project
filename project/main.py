import os
import shutil
from typing import Union
from pathlib import Path
from typing import List
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException,status
from pydantic import BaseModel, Field, conbytes
from uuid import UUID
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, time, timedelta, date

app = FastAPI()
from random import randrange
from . import crud, models, schemas
# import crud
# import models
# import schemas
from .database import SessionLocal, engine
from minio import Minio
from minio.error import S3Error

client = Minio(
    "172.19.0.5:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_user(db, email: str):
    user_dict = crud.get_users(db)
    if email in user_dict:
        user = db[email]
        return user

async def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):

    user = get_user(db,token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: schemas.User= Depends(get_current_user)):
    if current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
@app.get("/users/me")
async def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db,form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    hashed_password = str(form_data.password) + "somehash"
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    return {"access_token": user.email, "token_type": "bearer"}


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/frames/{code}")
def read_images(code: int, db: Session = Depends(get_db)):
    images = crud.get_image_by_id(db=db, send_id=code)
    if (len(images) == 0):
        raise HTTPException(status_code=404, detail="There is no images with that request code")
    return images


@app.delete("/frames/{code}")
def delete_images(code: int, db: Session = Depends(get_db)):
    images, time = crud.del_images(db=db, send_id=code)
    if (len(images) == 0):
        raise HTTPException(status_code=404, detail="There is no images with that request code")
    dt_string = time.strftime("%Y%m%d")
    for i in images:
        client.remove_object(dt_string, str(i))


@app.post("/frames/")
def post_image(files: List[UploadFile], db: Session = Depends(get_db)):
    print(len(files))
    if (len(files) > 15):
        raise HTTPException(status_code=405, detail="You can upload only 15 images ones")
    elif (len(files) == 0):
        raise HTTPException(status_code=405, detail="You have to put images to your request")
    else:
        code = randrange(1, 10000000)
        now = datetime.now()
        dt_string = now.strftime("%Y%m%d")
        for i in range(len(files)):
            name = str(uuid.uuid4()) + ".jpeg"
            crud.create_image(db=db, send_id=code, send_name=name, send_time=now)
            found = client.bucket_exists(dt_string)
            if not found:
                client.make_bucket(dt_string)
            client.fput_object(dt_string, name, files[i].file.fileno())
        images = crud.get_image_by_id(db=db, send_id=code)
        return images
