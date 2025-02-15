from dataclasses import dataclass, asdict

from . import models

@dataclass
class FileInStorageCloudSerializer:
    pk: int
    title: str
    uploader: str
    likes: int
    liked: bool
    downloads: int
    object_type: str = "pdf"
    recommended: bool = False

def file_in_storage_cloud_serializer(file: models.FileInCloudStorage, user: models.User) -> dict:
    liked = False
    if user: liked = True if user in file.likes else False

    return asdict(FileInStorageCloudSerializer(
            pk=file.pk, title=file.title, liked=liked,
            uploader=file.uploaded_by.telegram_id, likes=file.likes_count,
            downloads=file.downloads, recommended=file.is_promoted))


@dataclass
class DirectorySerializer:
    pk: int
    title: str
    parent_dir_pk: int

def directory_serializer(dir: models.Directory) -> dict:
    return asdict(DirectorySerializer(pk=dir.pk, title=dir.title, parent_dir_pk=dir.parent_dir_pk))
