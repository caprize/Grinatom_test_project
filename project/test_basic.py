from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from main import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_put_images():
    headers = {
        'accept': 'application/json',
        # requests won't add a boundary if this header is set when you pass files=
        # 'Content-Type': 'multipart/form-data',
    }

    files = {
        'files': open('/Users/caprize/Desktop/BD/bd1.png', 'rb'),
        'type': 'image/jpeg',
    }
    response = client.post(
        "/frames/",
        files=files,
        headers=headers
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "id" in data[0]
    code_id = data[0]["id"]

    response = client.get(f"/frames/{code_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data[0]["id"] == code_id

    response = client.delete(f"/frames/{code_id}")
    assert response.status_code == 200, response.text

test_put_images()
