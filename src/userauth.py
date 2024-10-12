import logging
from passlib.context import CryptContext
import re
from typing import Optional

import src.operations as backend
from src.models import User, UserFromDB


# silence a passlib/bcrypt warning
logging.getLogger("passlib").setLevel(logging.ERROR)

#
ANON_PREFIX = "anon:"
ANON_PATTERN = ANON_PREFIX + r"\d+"
GUEST_USER_KEY = backend.SETTINGS.guest_user_key

pw_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# User operations


def fetch_user(
    id: Optional[int] = None, email: Optional[str] = None, sub: Optional[str] = None
) -> UserFromDB | None:
    if sub:
        # recursive branch
        if re.fullmatch(ANON_PATTERN, sub):
            return fetch_user(id=sub.strip(ANON_PREFIX))
        else:
            return fetch_user(email=sub)
    elif email:
        user_dict = backend.DB.get_registered_user(email=email)
    elif id:
        user_dict = backend.DB.get_user(id=id)
    else:
        raise ValueError("Requires id, email, or token sub value")

    if user_dict:
        return UserFromDB(**user_dict)


def make_user_sub(user: User) -> str:
    return user.email or ANON_PREFIX + str(user.id)


def authenticate_user(user_email: str, pw: str) -> UserFromDB | None:
    user = fetch_user(email=user_email)
    if not user:
        return None
    if not verify_password(pw, user.password_hash):
        return None
    return user


def acceptable_user_creds(email: str, pw: str) -> bool:
    good_pw = len(pw) >= 6
    # TODO: validate better
    good_email = "@" in email
    return good_pw and good_email


def create_user(email: str, pw: str) -> int | None:
    # ensure username does not already exist
    if not backend.DB.get_registered_user(email=email):
        new_uid = backend.DB.add_registered_user(
            email=email, password_hash=hash_password(pw)
        )
        return new_uid


def create_guest_user(pw: str) -> UserFromDB | None:
    # use a password so guests are only created by system
    if pw == GUEST_USER_KEY:
        new_uid = backend.DB.add_anon_user()
        return fetch_user(id=new_uid)


# Password helpers


def verify_password(plain_password, hashed_password):
    return pw_context.verify(plain_password, hashed_password)


def hash_password(password):
    return pw_context.hash(password)
