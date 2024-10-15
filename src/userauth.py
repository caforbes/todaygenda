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
            return fetch_user(id=int(sub.strip(ANON_PREFIX)))
        else:
            return fetch_user(email=sub)
    elif email:
        user_dict = backend.DB.get_registered_user(email=email)
    elif id:
        user_dict = backend.DB.get_user(id=id)
    else:
        raise ValueError("Requires id, email, or token sub value")

    if user_dict:
        return UserFromDB(**user_dict)  # type: ignore
    return None


def make_user_sub(user: User) -> str:
    return user.email or ANON_PREFIX + str(user.id)


def authenticate_user(user_email: str, pw: str | None) -> UserFromDB | None:
    if not pw:
        return None

    user = fetch_user(email=user_email)
    if user and user.password_hash and verify_password(pw, user.password_hash):
        return user

    return None


def acceptable_user_creds(email: str, pw: str) -> bool:
    """Provide very basic validation checks for email structure and pw length."""
    email_pat = r"[^@\s]+@[^@\s]+\.[^@\s]+"  # general email structure: ___@__._
    good_email = re.fullmatch(email_pat, email)

    good_pw = len(pw) >= 6

    return bool(good_email and good_pw)


def create_user(email: str, pw: str) -> int | None:
    # ensure username does not already exist
    if backend.DB.get_registered_user(email=email):
        return None

    new_uid = backend.DB.add_registered_user(
        email=email, password_hash=hash_password(pw)
    )
    return new_uid


def create_guest_user(pw: str) -> UserFromDB | None:
    # use a password so guests are only created by system
    if pw != GUEST_USER_KEY:
        return None

    new_uid = backend.DB.add_anon_user()
    return fetch_user(id=new_uid)


# Password helpers


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pw_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pw_context.hash(password)
