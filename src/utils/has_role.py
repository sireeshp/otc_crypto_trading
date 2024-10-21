from typing import List

from src.models.AuthModel import User


def has_role(user: User, required_roles: List[str]):
    return bool(user.roles and any(role in required_roles for role in user.roles))
