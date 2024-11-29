from pathlib import Path

from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from sqladmin import Admin

from telegram.database.engine import engine
from .views import admin as admin_views


app = Starlette(debug=True)
admin_handler = Admin(app, engine, title="Qut Archive Admin", favicon_url="http://localhost:8000/static/images/logo-no-background.png")

app.router.routes.append(Mount("/static", app=StaticFiles(directory=Path("webapp/static")), name="static"))
admin_handler.add_view(admin_views.UserAdmin)
