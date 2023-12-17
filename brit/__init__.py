from os import getenv
from pathlib import Path

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette_login.backends import SessionAuthBackend
from starlette_login.middleware import AuthenticationMiddleware
from tinydb import TinyDB

from . import auth, pages

DEBUG = bool(getenv("DEBUG", False))
DATABASE = Path(getenv("DATABASE_FILE", "database.json"))

routes = [
    Route("/", pages.AllLists, name="all-shopping-lists"),
    Route("/{timestamp:float}", pages.SingleList, name="shopping-list"),
    Route("/new", pages.NewList, methods=["GET", "POST"], name="new-shopping-list"),
    Route("/sign-in", auth.SignIn, methods=["GET", "POST"], name="sign-in"),
    Route("/sign-up", auth.SignUp, methods=["GET", "POST"], name="sign-up"),
    Route("/sign-out", auth.SignOut, name="sign-out"),
    Mount("/static", app=StaticFiles(directory="brit/static"), name="static"),
]

app = Starlette(
    debug=DEBUG,
    routes=routes,
    middleware=[
        Middleware(SessionMiddleware, secret_key=auth.SECRET_KEY),
        Middleware(
            AuthenticationMiddleware,
            backend=SessionAuthBackend(auth.login_manager),
            login_manager=auth.login_manager,
        ),
    ],
)
app.state.login_manager = auth.login_manager
app.state.db = TinyDB(DATABASE)
