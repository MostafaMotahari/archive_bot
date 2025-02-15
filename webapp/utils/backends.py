from urllib.parse import unquote, parse_qs

from starlette.middleware.authentication import AuthenticationBackend, AuthCredentials, AuthenticationError
from starlette.requests import Request
from sqlalchemy import select

from webapp.utils.auth_tools import validate_init_data
from telegram.database.engine import async_session
from telegram.database.models import User


class TelegramHashBackend(AuthenticationBackend):
    async def init_auth(self, request: Request):
        if not request.query_params: raise AuthenticationError("No initData was fount!")

        if validate_init_data(request.query_params):
            async with async_session() as session:
                user_in_db = await session.scalars(select(User).where(User.telegram_id == request.query_params.get('user'))).one()
                user_in_db.telegram_hash = request.query_params.get('hash')
                request.sessio["user"] = user_in_db.telegram_hash
                session.commit()
                return AuthCredentials(['authenticated']), user_in_db
        raise AuthenticationError("The hash key is invalid!")

    async def check_auth(self, request: Request, user: str):
        async with async_session() as session:
            user_in_db = session.scalars(select(User).where(User.telegram_hash == user)).one() or False
            if user_in_db:
                return AuthCredentials(['authenticated']), user_in_db
            raise AuthenticationError("The hash key was not found!")

    async def authenticate(self, request: Request):
        user = request.session.get("user", None)
        if not user:
            return await self.init_auth(request)
        return await self.check_auth(request, user)


# from sqladmin.authentication import AuthenticationBackend
# from os import environ
# from typing import Union
# 
# from authlib.integrations.starlette_client import OAuth
# from starlette.responses import RedirectResponse, Response
# from telegram.database.models import ModeratorUser, User
# from telegram.database.engine import engine, async_session
# oauth = OAuth()
# oauth.register(
#     "google",
#     client_id=environ.get("GOOGLE_CLIENT_ID", "None"),
#     client_secret=environ.get("GOOGLE_CLIENT_SECRET", "None"),
#     server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
#     client_kwargs={
#         'scope': 'openid email profile',
#         'prompt': 'select_account',
#     },
# )
# google = oauth.create_client("google")
# 
# 
# class AdminPanelAuth(AuthenticationBackend):
#     async def login(self, request: Request) -> bool:
#         return True
# 
#     async def logout(self, request: Request) -> bool:
#         request.session.clear()
#         return True
# 
#     async def authenticate(self, request: Request) -> Union[bool, RedirectResponse]:
#         user = request.session.get('user')
#         print(request.cookies)
#         request.session['kos'] = "Koon"
#         if user:
#             async with engine.connect() as session:
#                 moderator_user = await session.scalar(select(ModeratorUser).where(ModeratorUser.email == user["email"]))
#                 if moderator_user:
#                     return True if moderator_user.is_active else False
#                 return False
# 
#         redirect_uri = request.url_for('login_google')
#         return await google.authorize_redirect(request, redirect_uri)
# 
# 
# async def login_google(request: Request) -> Response:
#     token = await google.authorize_access_token(request)
#     user = token.get('userinfo')
#     request.session['kos'] = "Koon"
#     if user:
#         request.session['user'] = user
#     return RedirectResponse(request.url_for("admin:index"))
