from typing import List
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    telegram_id: Mapped[str] = mapped_column(unique=True, index=True)
    semester: Mapped[int] = mapped_column(default=1)
    field_of_study: Mapped[str] = mapped_column()
    notifications: Mapped[bool] = mapped_column(default=True)


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
    title: Mapped[str] = mapped_column()
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
    creation_date: Mapped[datetime] = mapped_column(default=datetime.now())
    tags: Mapped[List["Tag"]] = relationship(secondary="tag_file_rel", back_populates="files")


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True)
    files: Mapped[List[FileInTelegramCloud]] = relationship(secondary="tag_file_rel", back_populates="tags")
    categories: Mapped[List["Category"]] = relationship(secondary="category_tag_rel", back_populates="tags")


class Log(Base):
    __tablename__ = "log"

    id: Mapped[int] = mapped_column(primary_key=True)
    level: Mapped[str] = mapped_column(index=True)
    text: Mapped[str] = mapped_column()
    time: Mapped[datetime] = mapped_column()


class Directory(Base):
    __tablename__ = "directory"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    parent_dir_id: Mapped[int] = mapped_column(ForeignKey("directory.id"), primary_key=True)
    parent_dir: Mapped[List["Directory"]] = relationship(back_populates="sub_directories")
