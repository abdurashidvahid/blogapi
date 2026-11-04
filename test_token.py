from mtoken import create_token, read_token
from jose import JWTError
import pytest



def test_token_tampered():
    token = create_token(5)
    tampered = token.rsplit(".", 1)[0] + ".abc"
    with pytest.raises(JWTError):
         read_token(tampered)

def test_token_round_trip():
    token = create_token(5)
    data = read_token(token)
    assert data["sub"] == "5"

def test_read_garbage_token():
    with pytest.raises(JWTError):
        read_token("not-a-token")