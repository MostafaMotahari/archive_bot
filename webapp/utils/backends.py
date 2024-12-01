from os import environ
from typing import Union

from sqladmin.authentication import AuthenticationBackend
from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse, Response
from starlette.requests import Request
from sqlalchemy import select

from telegram.database.models import ModeratorUser
from telegram.database.engine import engine


oauth = OAuth()
oauth.register(
    "google",
    client_id=environ.get("GOOGLE_CLIENT_ID", "None"),
    client_secret=environ.get("GOOGLE_CLIENT_SECRET", "None"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account',
    },
)
google = oauth.create_client("google")


class AdminPanelAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        return True

    async def logout(self, request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request) -> Union[bool, RedirectResponse]:
        user = request.session.get("user")
        if user:
            raise Exception(user)
            async with engine.connect() as session:
                moderator_user = await session.scalar(select(ModeratorUser).where(ModeratorUser.email == user["email"]))
                if moderator_user:
                    return True if moderator_user.is_active else False
                return False

        redirect_uri = request.url_for('login_google')
        return await google.authorize_redirect(request, redirect_uri)


async def login_google(request: Request) -> Response:
    token = await google.authorize_access_token(request)
    user = token.get('userinfo')
    raise Exception(user)
    if user:
        request.session['user'] = user
    return RedirectResponse(request.url_for("admin:index"))
