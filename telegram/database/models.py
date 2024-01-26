from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, BigInteger, Boolean, String, ForeignKey, Table
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List


Base = declarative_base()
metadata = Base.metadata


tag_doc_association_table = Table(
    "association_table",
    metadata,
    Column("document_id", ForeignKey("document.id"), primary_key=True),
    Column("tag_id", ForeignKey("tag.id"), primary_key=True),
)

class BotUser(Base):
    __tablename__ = "bot_user"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = Column(BigInteger, unique=True, index=True)
    uploaded_docs = Column(Integer, default=0)
    is_ban = Column(Boolean, default=False)
    documents: Mapped[List["Document"]] = relationship(back_populates="user")  
    receive_notifications = Column(Boolean, default=True)
    study_field = Column(String, nullable=True)
    is_superuser = Column(Boolean, default=False)
    permissions = Column(String, nullable=True)

    def get_all_permissions(self):
        return self.permissions.split(',')

    def has_permission(self, permission: str):
        return permission in self.permissions


class Statistics(Base):
    __tablename__ = "statistics"

    id = Column(Integer, unique=True, primary_key=True)
    users_count = Column(Integer, default=0)
    downloaded = Column(BigInteger, default=0)
    uploaded = Column(BigInteger, default=0)


class Document(Base):
    __tablename__ = "document"

    id: Mapped[int] = mapped_column(primary_key=True)
    title = Column(String, unique=True, index=True)
    persian_title = Column(String)
    path = Column(String, unique=True)
    download_count = Column(Integer, default=0)
    file_id = Column(String, unique=True, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("bot_user.id"), nullable=True) 
    user: Mapped["BotUser"] = relationship(back_populates="documents")
    directory_id: Mapped[int] = mapped_column(ForeignKey("directory.id"))
    directory: Mapped["Directory"] = relationship(back_populates="documents")
    tags: Mapped[List["Tag"]] = relationship(secondary=tag_doc_association_table, back_populates="documents")


class Directory(Base):
    __tablename__ = "directory"

    id: Mapped[int] = mapped_column(primary_key=True)
    name = Column(String, unique=True, index=True)
    persian_title = Column(String)
    parent_id: Mapped[int] = mapped_column(ForeignKey("directory.id"), nullable=True)
    parent: Mapped["Directory"] = relationship(back_populates="sub_directories", remote_side=[id])
    sub_directories: Mapped[List["Directory"]] = relationship(back_populates="parent", cascade="all")
    documents: Mapped[List["Document"]] = relationship(back_populates="directory", cascade="all")


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True)
    name = Column(String, unique=True, index=True)
    documents: Mapped[List[Document]] = relationship(secondary=tag_doc_association_table, back_populates="tags")
