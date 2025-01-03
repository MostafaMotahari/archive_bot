from typing import List, Optional
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    pass


class ModeratorUser(Base):
    __tablename__ = "moderator_user"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str] = mapped_column()
    auth_token: Mapped[str] = mapped_column(nullable=True)
    permission: Mapped[str] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)
    user: Mapped["User"] = relationship(back_populates="moderator_user")
    verified_files: Mapped[List["FileInTelegramCloud"]] = relationship(back_populates="verified_by")


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    telegram_id: Mapped[str] = mapped_column(unique=True, index=True)
    semester: Mapped[int] = mapped_column(default=1)
    field_of_study: Mapped[str] = mapped_column()
    notifications: Mapped[bool] = mapped_column(default=True)
    moderator_user_id: Mapped[int] = mapped_column(ForeignKey("moderator_user.id"), unique=True)
    moderator_user: Mapped["ModeratorUser"] = relationship(back_populates="user", single_parent=True)
    history: Mapped["UserHistory"] = relationship(back_populates="user")


class Statistics(Base):
    __tablename__ = "statistics"

    id: Mapped[int] = mapped_column(primary_key=True)
    users_count: Mapped[int] = mapped_column(default=0)


class CategoryTagRel(Base):
    __tablename__ = "category_tag_rel"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tag.id"), primary_key=True)


class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True)
    tags: Mapped[List["Tag"]] = relationship(secondary="category_tag_rel", back_populates="categories")


class TagFileRel(Base):
    __tablename__ = "tag_file_rel"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_id: Mapped[int] = mapped_column(ForeignKey("file_in_telegram_cloud.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tag.id"), primary_key=True)


class FileInTelegramCloud(Base):
    __tablename__ = "file_in_telegram_cloud"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True)
    file_id: Mapped[str] = mapped_column(index=True)
    description: Mapped[str] = mapped_column()
    tags: Mapped[List["Tag"]] = relationship(secondary="tag_file_rel", back_populates="files")
    verification_time: Mapped[datetime] = mapped_column(default=datetime.now())
    verified_by_id: Mapped[int] = mapped_column(ForeignKey("moderator_user.id"))
    verified_by: Mapped[ModeratorUser] = relationship(back_populates="verified_files")
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teacher_cv.id"))
    teacher: Mapped["TeacherCV"] = relationship(back_populates="files")
    histories: Mapped[List["UserHistory"]] = relationship(back_populates="files")


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True)
    files: Mapped[List[FileInTelegramCloud]] = relationship(secondary="tag_file_rel", back_populates="tags")
    categories: Mapped[List["Category"]] = relationship(secondary="category_tag_rel", back_populates="")


class Log(Base):
    __tablename__ = "log"

    id: Mapped[int] = mapped_column(primary_key=True)
    level: Mapped[str] = mapped_column(index=True)
    text: Mapped[str] = mapped_column()
    time: Mapped[datetime] = mapped_column()


class Directory(Base):
    __tablename__ = "directory"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True)
    parent_dir_id: Mapped[Optional[int]] = mapped_column(ForeignKey("directory.id"))
    parent_dir: Mapped[Optional["Directory"]] = relationship(back_populates="sub_directories", remote_side=[id])
    sub_directories: Mapped[List["Directory"]] = relationship(back_populates="parent_dir")


class TeacherCV(Base):
    __tablename__ = "teacher_cv"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(index=True)
    files: Mapped[List["FileInTelegramCloud"]] = relationship(back_populates="teacher")


class UserHistory(Base):
    __tablename__ = "user_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), unique=True)
    user: Mapped[User] = relationship(back_populates="history", single_parent=True)
    file_id: Mapped[int] = mapped_column(ForeignKey("file_in_telegram_cloud.id"))
    file: Mapped[FileInTelegramCloud] = relationship(back_populates="histories")
