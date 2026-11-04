from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mainapi import app,get_session
from smain import Base
import pytest


engine = create_engine("sqlite:///test.db")

TestSession = sessionmaker(bind=engine)
client = TestClient(app) #creates the fake browser, pointed at your app.

def override_get_session():
    db = TestSession()
    try: 
        yield db
    finally:
        db.close()
#use override instead of get session when u run fastapi files, 
app.dependency_overrides[get_session] = override_get_session


#refreshing the db 
@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture   
def register():
    user = {"username": "gulishka", "email":"gulishka", "password": "gulishka89"}
    response = client.post("/register", json=user)
    assert response.status_code == 200



def test_login(register):
    login = client.post("/login", json= {"email": "gulishka", "password": "gulishka89"})
    assert login.status_code == 200
    assert "access_token" in login.json() 
    token =  login.json()["access_token"]
    return token

def test_register_duplicate(register):
    dup_reg = client.post("/register", json={"username": "gulishka", "email":"gulishka", "password": "gulishka89"})
    assert dup_reg.status_code == 409

def test_wrong_password(register):
    login = client.post("/login", json={"email":"gulishka", "password": "gulishka69"})
    assert login.status_code == 401


def get_token(email):
    user = {"username": email ,"email": email, "password":"gulishka89"}
    r= client.post("/register", json=user)
    assert r.status_code == 200
    login = client.post("/login", json={"email": email, "password":"gulishka89"})
    assert login.status_code == 200
    return login.json()["access_token"]


def test_post():
    token_a = get_token("aron")
    token_b = get_token("guli")
    post = {"content": "Hello"}
    r = client.post("/posts", json=post, headers={"Authorization": f"Bearer {token_a}"})
    assert r.status_code == 200
    post_id = r.json()["id"]
    d = client.delete(f"/posts/{post_id}",headers={"Authorization": f"Bearer {token_b}"} )
    assert d.status_code == 403
    own = client.delete(f"/posts/{post_id}",headers={"Authorization": f"Bearer {token_a}"} )
    assert own.status_code == 200
    if_miss = 2
    missing = client.delete(f"/posts/{if_miss}",headers={"Authorization": f"Bearer {token_a}"} )
    assert missing.status_code == 404


    