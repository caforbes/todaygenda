from api.routes.auth import build_token_object
from src.models import User


def auth_headers(user_dict: dict) -> dict:
    user = User(**user_dict)
    token = build_token_object(user).access_token
    headers = {"Authorization": f"Bearer {token}"}
    return headers
