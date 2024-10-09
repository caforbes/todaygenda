from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt

from src.userauth import (
    authenticate_user,
    create_user,
    create_guest_user,
    fetch_user,
    make_user_sub,
)
import src.operations as backend
from src.models import User, UserFromDB, Token, TokenData


ALGORITHM = "HS256"  # FIX: use "ES256"
ACCESS_TOKEN_EXPIRE_MINS = 30
SECRET_KEY = backend.SETTINGS.secret_key

router = APIRouter(prefix="/user")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/token")


# Token/JWT handling


def create_token(data: dict, expires_delta: timedelta | None = None):
    data_to_encode = data.copy()
    if expires_delta:
        expiry = datetime.now(timezone.utc) + expires_delta
    else:
        expiry = datetime.now(timezone.utc) + timedelta(minutes=15)
    data_to_encode.update({"exp": expiry})

    encoded_jwt = jwt.encode(data_to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Auth functions


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserFromDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # decode token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_sub: str = payload.get("sub")
        if user_sub is None:
            raise credentials_exception
        token_data = TokenData(user_sub=user_sub)
    except jwt.InvalidTokenError:
        raise credentials_exception

    # check if the user is registered or guest, retrieve them accordingly
    user = fetch_user(sub=token_data.user_sub)

    if user is None:
        raise credentials_exception

    # return user object
    return user


def get_current_registered_user(
    current_user: Annotated[UserFromDB, Depends(get_current_user)]
) -> UserFromDB:
    if not current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires full user registration",
        )
    return current_user


# Routes


@router.get("/", response_model=User)
def read_user(current_user: Annotated[UserFromDB, Depends(get_current_user)]):
    # TODO: test password NOT IN RESPONSE
    return current_user


# TODO: signup endpoint
@router.post("/")
def register_new_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> int:
    new_uid = create_user(email=form_data.username, pw=form_data.password)
    if not new_uid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username or password details provided during registration",
        )

    # TODO: return auth???
    # return login_token(form_data=form_data)
    return new_uid


# TODO: anonymous signup endpoint
def populate_anon_user_creds():
    pass


@router.post("/token")
def login_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    bad_login_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Incorrect username or password",
    )

    # validate credentials or create temp user
    if form_data.username == "anonymous":
        user = create_guest_user(form_data)
    else:
        user = authenticate_user(user_email=form_data.username, pw=form_data.password)

    if not user:
        raise bad_login_error

    user_sub = make_user_sub(user)

    # build access token
    token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINS)
    access_token = create_token(data={"sub": user_sub}, expires_delta=token_expires)
    return Token(access_token=access_token, token_type="bearer")
