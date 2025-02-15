from typing import List, Optional
from datetime import datetime

from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    pass


class StorageFileUserLikeRel(Base):
    __tablename__ = "storage_file_user_like_rel"

    pk: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    file_in_cloud_storage_pk: Mapped[int] = mapped_column(ForeignKey("file_in_cloud_storage.pk"), primary_key=True)
    user_pk: Mapped[int] = mapped_column(ForeignKey("users.pk"), primary_key=True)


class ModeratorUser(Base):
    __tablename__ = "moderator_user"

    pk: Mapped[int] = mapped_column(primary_key=True, unique=True)
    full_name: Mapped[Optional[str]] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str] = mapped_column()
    permission: Mapped[str] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)
    user: Mapped["User"] = relationship(back_populates="moderator_user")
    verified_files: Mapped[List["FileInCloudStorage"]] = relationship(back_populates="verified_by")

    def __str__(self):
        return self.full_name or "Unknown"

    @property
    def uploaded_files_count(self):
        if self.user: return len(self.user.uploaded_files)
        return 0

    @property
    def verified_files_count(self):
        return len(self.verified_files)


class User(Base):
    __tablename__ = 'users'

    pk: Mapped[int] = mapped_column(primary_key=True, unique=True)
    telegram_id: Mapped[str] = mapped_column(unique=True, index=True)
    telegram_hash: Mapped[Optional[str]] = mapped_column(nullable=True)
    semester: Mapped[int] = mapped_column(default=1)
    field_of_study: Mapped[str] = mapped_column()
    notifications: Mapped[bool] = mapped_column(default=True)
    moderator_user_pk: Mapped[Optional[int]] = mapped_column(ForeignKey("moderator_user.pk"), unique=True, nullable=True)
    moderator_user: Mapped[Optional["ModeratorUser"]] = relationship(back_populates="user", single_parent=True)
    liked_files: Mapped[Optional[List["FileInCloudStorage"]]] = relationship(secondary="storage_file_user_like_rel", back_populates="likes")
    uploaded_files: Mapped[Optional[List["FileInCloudStorage"]]] = relationship(back_populates="uploaded_by")

    def __str__(self):
        if self.field_of_study: return self.telegram_id + ' - ' + self.field_of_study
        return self.telegram_id

    @property
    def uploaded_files_count(self):
        return len(self.uploaded_files)


class Statistics(Base):
    __tablename__ = "statistics"

    pk: Mapped[int] = mapped_column(primary_key=True)
    users_count: Mapped[int] = mapped_column(default=0)


class CategoryTagRel(Base):
    __tablename__ = "category_tag_rel"

    pk: Mapped[int] = mapped_column(primary_key=True)
    category_pk: Mapped[int] = mapped_column(ForeignKey("category.pk"), primary_key=True)
    tag_pk: Mapped[int] = mapped_column(ForeignKey("tag.pk"), primary_key=True)


class Category(Base):
    __tablename__ = "category"

    pk: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True)
    tags: Mapped[List["Tag"]] = relationship(secondary="category_tag_rel", back_populates="categories")

    def __str__(self):
        return self.title


class TagFileRel(Base):
    __tablename__ = "tag_file_rel"

    pk: Mapped[int] = mapped_column(primary_key=True)
    file_pk: Mapped[int] = mapped_column(ForeignKey("file_in_cloud_storage.pk"), primary_key=True)
    tag_pk: Mapped[int] = mapped_column(ForeignKey("tag.pk"), primary_key=True)


class FileInCloudStorage(Base):
    __tablename__ = "file_in_cloud_storage"
    __table_args__ = (CheckConstraint("""(is_active = TRUE AND title IS NOT NULL AND description IS NOT NULL) OR
                                      (is_active = FALSE AND (title IS NULL OR description IS NULL))"""),)

    pk: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True, nullable=True)
    description: Mapped[str] = mapped_column(nullable=True)
    tags: Mapped[List["Tag"]] = relationship(secondary="tag_file_rel", back_populates="files")
    is_active: Mapped[bool] = mapped_column(default=False)

    hard_uploaded: Mapped[bool] = mapped_column(default=False)
    is_promoted: Mapped[bool] = mapped_column(default=False)
    likes: Mapped[Optional[List["User"]]] = relationship(secondary="storage_file_user_like_rel", back_populates="liked_files")
    downloads: Mapped[int] = mapped_column(default=0)

    upload_datetime: Mapped[datetime] = mapped_column(default=datetime.now())
    uploaded_by_pk: Mapped[int] = mapped_column(ForeignKey("users.pk"))
    uploaded_by: Mapped["User"] = relationship(back_populates="uploaded_files")

    directory_pk: Mapped[Optional[int]] = mapped_column(ForeignKey("directory.pk"), nullable=True)
    directory: Mapped[Optional["Directory"]] = relationship(back_populates="files")

    raw_location: Mapped[str] = mapped_column(nullable=False, unique=True)
    telegram_cloud: Mapped[Optional["FileInTelegramCloud"]] = relationship(back_populates="storage")

    verification_time: Mapped[Optional[datetime]] = mapped_column(default=datetime.now(), nullable=True)
    verified_by_pk: Mapped[int] = mapped_column(ForeignKey("moderator_user.pk"))
    verified_by: Mapped["ModeratorUser"] = relationship(back_populates="verified_files")

    teacher_pk: Mapped[Optional[int]] = mapped_column(ForeignKey("teacher_cv.pk"), nullable=True)
    teacher: Mapped[Optional["TeacherCV"]] = relationship(back_populates="files")

    def __str__(self):
        return self.title or self.raw_location

    @property
    def likes_count(self):
        return len(self.likes)


class FileInTelegramCloud(Base):
    __tablename__ = "file_in_telegram_cloud"

    pk: Mapped[int] = mapped_column(primary_key=True)
    in_tel_title: Mapped[str] = mapped_column(index=True)
    file_pk: Mapped[str] = mapped_column(index=True)

    storage_pk: Mapped[int] = mapped_column(ForeignKey("file_in_cloud_storage.pk"), unique=True)
    storage: Mapped[FileInCloudStorage] = relationship(back_populates="telegram_cloud", single_parent=True)

    def __str__(self):
        return self.in_tel_title


class Tag(Base):
    __tablename__ = "tag"

    pk: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True)
    files: Mapped[List[FileInCloudStorage]] = relationship(secondary="tag_file_rel", back_populates="tags")
    categories: Mapped[List["Category"]] = relationship(secondary="category_tag_rel", back_populates="")

    def __str__(self):
        return self.title


class Log(Base):
    __tablename__ = "log"

    pk: Mapped[int] = mapped_column(primary_key=True)
    level: Mapped[str] = mapped_column(index=True)
    text: Mapped[str] = mapped_column()
    time: Mapped[datetime] = mapped_column()


class Directory(Base):
    __tablename__ = "directory"

    pk: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(unique=True, index=True)
    title: Mapped[str] = mapped_column(index=True)
    parent_dir_pk: Mapped[Optional[int]] = mapped_column(ForeignKey("directory.pk"), nullable=True)
    parent_dir: Mapped[Optional["Directory"]] = relationship(back_populates="sub_directories", remote_side=[pk])
    sub_directories: Mapped[List["Directory"]] = relationship(back_populates="parent_dir")

    files: Mapped[Optional[List[FileInCloudStorage]]] = relationship(back_populates="directory")

    def __str__(self):
        return self.title

    @property
    def items_count(self):
        return len(self.files) + len(self.sub_directories)


class TeacherCV(Base):
    __tablename__ = "teacher_cv"

    pk: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(index=True)
    files: Mapped[Optional[List["FileInCloudStorage"]]] = relationship(back_populates="teacher")

    def __str__(self):
        return self.full_name
