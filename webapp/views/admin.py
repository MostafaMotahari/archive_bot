from sqladmin import ModelView

from telegram.database import models


class UserAdmin(ModelView, model=models.User):
    column_list = [models.User.pk, models.User.telegram_id, "uploaded_file_count"]


class ModeratorUserAdmin(ModelView, model=models.ModeratorUser):
    column_list = [models.ModeratorUser.pk, models.ModeratorUser.full_name,
                   "uploaded_file_count", "verified_files_count"]
    form_excluded_columns = [models.ModeratorUser.user]


class CategoryAdmin(ModelView, model=models.Category):
    column_list = [models.Category.pk, models.Category.title]


class TagAdmin(ModelView, model=models.Tag):
    column_list = [models.Tag.pk, models.Tag.title]


class FileInCloudStorageAdmin(ModelView, model=models.FileInCloudStorage):
    column_list = [models.FileInCloudStorage.pk, models.FileInCloudStorage.title, models.FileInCloudStorage.directory]
    form_excluded_columns = [models.FileInCloudStorage.telegram_cloud]


class DirectoryAdmin(ModelView, model=models.Directory):
    column_list = [models.Directory.pk, models.Directory.parent_dir, "files_count"]
    form_excluded_columns = [models.Directory.files]
