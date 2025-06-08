from sqlalchemy import Engine, ForeignKey, create_engine, Column, Table, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

class Base(DeclarativeBase):
    pass

class Message(Base):
    #also can be added for time 
    __tablename__ = "message"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="messages")
    chat_id: Mapped[int] = mapped_column(ForeignKey("chat.id"))
    chat: Mapped["Chat"] = relationship(back_populates="messages")

class Chat(Base):
    __tablename__ = "chat"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    users: Mapped[list["User"]] = relationship(secondary="chat_user", back_populates="chats")
    messages: Mapped[list["Message"]] = relationship(back_populates="chat")

class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()
    chats: Mapped[list["Chat"]] = relationship(secondary="chat_user", back_populates="users")
    messages: Mapped[list["Message"]] = relationship(back_populates="user")

# chat_user table for association between chats and users

chat_user = Table(
    "chat_user",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("chat_id", ForeignKey("chat.id"), primary_key=True)
)

