from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt

from api.utils import error_detail
from src.userauth import (
    acceptable_user_creds,
    authenticate_user,
    create_user,
    create_guest_user,
    fetch_user,
    make_user_sub,
    populate_guest_user,
)
import src.operations as backend
from src.models import ActionResult, User, UserFromDB, Token, TokenData


ALGORITHM = "HS256"
ACCESS_TOKEN_GUEST_EXPIRE_MINS = 24 * 60
ACCESS_TOKEN_EXPIRE_MINS = ACCESS_TOKEN_GUEST_EXPIRE_MINS * 7
SECRET_KEY = backend.SETTINGS.secret_key

router = APIRouter(prefix="/user")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/token")


# Token/JWT handling


def build_token_object(user: User) -> Token:
    user_sub = make_user_sub(user)
    if user.email:
        token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINS)
    else:
        token_expires = timedelta(minutes=ACCESS_TOKEN_GUEST_EXPIRE_MINS)
    access_token = create_token(data={"sub": user_sub}, expires_delta=token_expires)
    return Token(access_token=access_token, token_type="bearer")


def create_token(data: dict, expires_delta: timedelta | None = None) -> str:
    data_to_encode = data.copy()
    if expires_delta:
        expiry = datetime.now(timezone.utc) + expires_delta
    else:
        expiry = datetime.now(timezone.utc) + timedelta(minutes=15)
    data_to_encode.update({"exp": expiry})

    encoded_jwt = jwt.encode(data_to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Errors


INSUFFICIENT_EMAIL_PW_ERROR = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail=error_detail("Email or password did not meet requirements"),
)
REGISTRATION_ERROR = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail=error_detail("Registration not processed: Email may already be in use"),
)


# Auth functions


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserFromDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=error_detail("Could not validate credentials"),
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

    return user


def get_current_anon_user(
    current_user: Annotated[UserFromDB, Depends(get_current_user)]
) -> UserFromDB:
    if current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_detail("This action is restricted to guest users"),
        )
    return current_user


# Routes


@router.get("/", response_model=User, summary="Read user details")
def read_user(current_user: Annotated[UserFromDB, Depends(get_current_user)]):
    """Read details for the currently logged-in user."""
    return current_user


@router.post("/", summary="Sign up as a new user")
def register_new_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """Create a new user with by providing an email and password.

    * `username`: Must be a valid email address not yet registered in the system
    * `password`: Must be at least 6 characters
    """
    if not acceptable_user_creds(email=form_data.username, pw=form_data.password):
        raise INSUFFICIENT_EMAIL_PW_ERROR

    new_uid = create_user(email=form_data.username, pw=form_data.password)
    if not new_uid:
        raise REGISTRATION_ERROR

    return login_token(form_data)


@router.post("/register", summary="Sign up (for guest users)")
def populate_anon_user_creds(
    current_user: Annotated[UserFromDB, Depends(get_current_anon_user)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> ActionResult:
    """Guest users can create a permanent account by adding their email and password.

    * `username`: Must be a valid email address not yet registered in the system
    * `password`: Must be at least 6 characters

    It's recommended that users request a new token after performing this operation.
    """
    creds_data = {"email": form_data.username, "pw": form_data.password}
    # ensure only guest users can do this (reg users should edit details differently)
    if not acceptable_user_creds(**creds_data):
        raise INSUFFICIENT_EMAIL_PW_ERROR

    # edit user to add credentials
    result = populate_guest_user(current_user, **creds_data)
    if not result:
        raise REGISTRATION_ERROR

    return ActionResult(success=[current_user.id])


@router.post("/token", summary="Login to get an access token")
def login_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    """Get an access token by logging in with email and password.

    * `username`: Must be a valid email address registered on the system
    * `password`: The password associated with this email account
    """
    # validate credentials or create temp user
    if form_data.username == "anonymous":
        user = create_guest_user(pw=form_data.password)
    else:
        user = authenticate_user(user_email=form_data.username, pw=form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_detail("Incorrect username or password"),
            headers={"WWW-Authenticate": "Bearer"},
        )

    # build access token
    return build_token_object(user=user)
