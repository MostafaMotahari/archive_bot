from pathlib import Path
from os import environ

from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqladmin import Admin

from telegram.database.engine import engine
from .utils.backends import AdminPanelAuth, login_google
from .views import admin as admin_views

app = Starlette(debug=True)
app.add_middleware(SessionMiddleware, secret_key=environ.get("SESSION_SECRET_KEY", "None"), max_age=24*60*60, https_only=False)

admin_handler = Admin(
    app,
    engine,
    authentication_backend=AdminPanelAuth(secret_key="1234"),
    title="Qut Archive Admin",
    favicon_url=f"http://{environ.get('SITE_URL', 'localhost:8000')}/static/images/logo-no-background.png")

app.router.routes.append(Mount("/static", app=StaticFiles(directory=Path("webapp/static")), name="static"))
admin_handler.add_view(admin_views.UserAdmin)
admin_handler.app.router.add_route('/auth/google', login_google)
