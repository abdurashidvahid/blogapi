# Blog API

A REST API for a simple blog, built with FastAPI and SQLAlchemy. Users can register, log in with JWT authentication, and manage their own posts.

## Features

- User registration with hashed passwords (Argon2)
- Login with JWT access tokens
- Create and delete posts (authenticated)
- Ownership rules: only the author can delete their post (403 for others, 404 for missing posts)
- Automated tests with pytest on a separate test database

## Tech stack

- Python, FastAPI, Pydantic
- SQLAlchemy ORM
- JWT (python-jose), password hashing (pwdlib)
- pytest + FastAPI TestClient

## Project structure

```
mainapi.py        # FastAPI app and routes
smain.py          # SQLAlchemy models and database setup
mtoken.py         # JWT create/read helpers
test_api.py       # API tests (register, login, ownership)
test_mtoken.py    # Token helper tests
requirements.txt
```

## Run locally

1. Clone the repo and create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   pip install -r requirements.txt
   ```
2. Create a `blogkey.env` file next to `mainapi.py` with your own secret key:
   ```
   SECRET_KEY=your-long-random-string
   ```
3. Start the server:
   ```bash
   uvicorn mainapi:app --reload
   ```
4. Open the interactive docs at http://127.0.0.1:8000/docs

## Run the tests

```bash
python -m pytest -v
```

Tests use a separate `test.db`, which is created and wiped for every test.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/register` | Create a user (409 if the email exists) |
| POST | `/login` | Get an access token (401 on wrong credentials) |
| POST | `/posts` | Create a post (requires token) |
| DELETE | `/posts/{id}` | Delete your own post (403 if not the author, 404 if missing) |
