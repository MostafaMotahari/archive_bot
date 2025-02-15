from pathlib import Path
from os import environ

from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware import Middleware
from starlette.routing import Route
from sqladmin import Admin

from telegram.database.engine import engine
from .utils.backends import TelegramHashBackend
from .views import admin as admin_views
from .views import file_manager as file_manager_views


routes = [
    Route("/file_manager_home", endpoint=file_manager_views.file_manager_home, name="file_manager"),
    Route("/file_manager_alter", endpoint=file_manager_views.file_manager_retrieve, name="file_manager_retrieve_home"),
    Route("/file_manager_alter/{dir_pk:str}/{tg_id:str}", endpoint=file_manager_views.file_manager_retrieve, name="file_manager_retrieve_sub"),
]

middleware = [
    Middleware(SessionMiddleware, secret_key=environ.get("SESSION_SECRET_KEY", "None")),
    Middleware(AuthenticationMiddleware, backend=TelegramHashBackend()),
]

app = Starlette(debug=True, routes=routes, middleware=middleware)
# app.add_middleware(SessionMiddleware, secret_key=environ.get("SESSION_SECRET_KEY", "None"), max_age=24*60*60, https_only=False)

admin_handler = Admin(
    app, engine, title="Qut Archive Admin",
    favicon_url=f"http://{environ.get('SITE_URL', 'localhost:8000')}/static/images/logo-no-background.png")

app.router.routes.append(Mount("/static", app=StaticFiles(directory=Path("webapp/static")), name="static"))

admin_handler.add_view(admin_views.UserAdmin)
admin_handler.add_view(admin_views.ModeratorUserAdmin)
admin_handler.add_view(admin_views.CategoryAdmin)
admin_handler.add_view(admin_views.TagAdmin)
admin_handler.add_view(admin_views.FileInCloudStorageAdmin)
admin_handler.add_view(admin_views.DirectoryAdmin)
