from jose import jwt
import os
from dotenv import load_dotenv
from datetime import datetime,timedelta,timezone
load_dotenv("blogkey.env")
sec_key=os.getenv("SEC_KEY")
alg ="HS256"

def create_token(user_id):
    payload = {"sub":str(user_id), 
               "exp": datetime.now(timezone.utc) + timedelta(minutes=40)}
    token = jwt.encode(payload, sec_key,alg)
    return token


def read_token(token):
    readed = jwt.decode(token, sec_key, algorithms=[alg])
    return readed


    