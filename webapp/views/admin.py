from sqladmin import ModelView

from telegram.database import models


class UserAdmin(ModelView, model=models.User):
    column_list = [models.User.id, models.User.telegram_id]
