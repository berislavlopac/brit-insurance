import base64
import hashlib
from http import HTTPStatus
from random import randint

import bcrypt
from pydantic import BaseModel, EmailStr
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette_login.login_manager import LoginManager
from starlette_login.mixins import UserMixin
from starlette_login.utils import login_user, logout_user
from tinydb import Query

from .templates import templates

SECRET_KEY = ""


class User(BaseModel, UserMixin):
    email: EmailStr
    password: str

    @property
    def identity(self) -> str:
        return self.email

    @property
    def display_name(self) -> str:
        return self.email


class SignIn(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        if request.user.is_authenticated:
            next_url = request.query_params.get("next", request.url_for("all-shopping-lists"))
            return RedirectResponse(next_url, HTTPStatus.FOUND)
        return templates.TemplateResponse(request, "signin.html.jinja")

    async def post(self, request: Request) -> Response:
        async with request.form() as form_data:
            user = get_user_by_email(request, str(form_data["email"]))
            if user is None or _check_password(user, str(form_data["password"])) is False:
                return templates.TemplateResponse(
                    request,
                    "signin.html.jinja",
                    {"error_message": "Incorrect login credentials."},
                )
        await login_user(request, user)
        next_url = request.query_params.get("next", request.url_for("all-shopping-lists"))
        return RedirectResponse(next_url, HTTPStatus.SEE_OTHER)


class SignUp(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        return templates.TemplateResponse(request, "signup.html.jinja")

    async def post(self, request: Request) -> Response:
        async with request.form() as form_data:
            email = str(form_data["email"])
            user = get_user_by_email(request, email)
            if user is None:
                password = _generate_password_hash(str(form_data["password"]))
                user = User(email=email, password=password)
                request.app.state.db.insert(user.model_dump())
            else:
                return templates.TemplateResponse(
                    request, "signin.html.jinja", {"error_message": "User already exists."}
                )
        await login_user(request, user)
        return RedirectResponse(request.url_for("all-shopping-lists"), HTTPStatus.SEE_OTHER)


class SignOut(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        await logout_user(request)
        return RedirectResponse("sign-in")


login_manager = LoginManager(redirect_to="sign-in", secret_key=SECRET_KEY)


def get_user_by_email(request: Request, email: str) -> User | None:
    db = request.app.state.db
    users = db.search(Query().email == email)
    return None if not users else User(**users[0])


login_manager.set_user_loader(get_user_by_email)


def _check_password(user: User, password: str) -> bool:
    password_hash, salt, rounds = user.password.split("|")
    return _generate_password_hash(password, salt.encode(), int(rounds)) == user.password


def _generate_password_hash(
    password: str, salt: bytes | None = None, rounds: int | None = None
) -> str:
    password_bytes = base64.b64encode(hashlib.sha256(password.encode()).digest())
    if salt is None:
        salt = bcrypt.gensalt()
    if rounds is None:
        rounds = randint(128, 256)
    password_hash = bcrypt.kdf(password_bytes, salt=salt, desired_key_bytes=32, rounds=rounds)
    password_hash = base64.b64encode(password_hash)
    return f"{password_hash.decode()}|{salt.decode()}|{rounds}"
