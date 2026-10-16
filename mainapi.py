from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from pydantic import BaseModel,ConfigDict
from smain import get_session, Session, User,Post
from pwdlib import PasswordHash
from sqlalchemy.exc import IntegrityError #for email repeating error!
from mtoken import create_token,read_token
from jose import jwt
import os

sec_key=os.getenv("SEC_KEY")
alg ="HS256"
app = FastAPI()
ph = PasswordHash.recommended()
bearer = HTTPBearer()


class UserIn(BaseModel):
    username:str
    email:str
    password:str

class UserOut(BaseModel):
    id:int 
    email:str
    username: str
    model_config = ConfigDict(from_attributes=True)

class LogIn(BaseModel):
    email:str
    password:str

class PostIn(BaseModel):
    content:str

class PostOut(BaseModel):
    id:int
    content:str
    user_id:int
    model_config = ConfigDict(from_attributes=True)

def current_user(creds:HTTPAuthorizationCredentials = Depends(bearer),db:Session=Depends(get_session)):
    token = creds.credentials
    try:
        payload =  read_token(token)
        user_id = payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token") 
    user = db.get(User, int(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid tokens")
    return user 


@app.post("/register")
def user_register(user:UserIn, db:Session = Depends(get_session)):
    hashed = ph.hash(user.password)
    new_user =  User(username=user.username, email= user.email, hashed_password = hashed)
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409,detail="Email already registered" )
    db.refresh(new_user)
    return new_user


@app.post("/login")
def user_login(login:LogIn, db:Session=Depends(get_session)):
    login.email = login.email.lower()
    user = db.query(User).filter(User.email == login.email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not ph.verify(login.password, user.hashed_password):
        raise HTTPException(status_code=401, detail = "Invalid credintals")
    token = create_token(user.id)
    return {"access_token":token , "token type": "bearer"}

@app.post("/posts", response_model=PostOut)
def create_post(post:PostIn, db:Session= Depends(get_session), user:User= Depends(current_user)):
    new_post = Post(content = post.content, user_id = user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@app.get("/me", response_model=UserOut)
def me(user: User = Depends(current_user)):
    return user


@app.get("/me/posts", response_model=list[PostOut])
def get_post( db:Session = Depends(get_session), user: User=Depends(current_user)):
    posts = db.query(Post).filter(Post.user_id == user.id).all()
    return posts

@app.delete("/posts/{post_id}", response_model=PostOut)
def delete_post(post_id:int , db:Session= Depends(get_session), user:User = Depends(current_user)):
    post = db.get(Post,post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="No such post")
    if post.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your post")
    db.delete(post)
    db.commit()
    return "Post Deleted"


@app.patch("/posts/{post_id}", response_model=PostOut)
def post_patch(post_id:int,post:PostIn,db:Session = Depends(get_session), user:User = Depends(current_user)):
    patched = db.get(Post,post_id)
    if patched is None:
        raise HTTPException(status_code=404 , detail="No such post")
    if patched.user_id != user.id:
        raise HTTPException(status_code=403,detail="Not your post")
    patched.content = post.content
    db.commit()
    db.refresh(patched)
    return patched