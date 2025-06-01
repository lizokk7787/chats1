import tkinter
import tkinter.ttk
import flask
import hashlib
from database import User, Message, Chat, chat_user

from sqlalchemy import Engine, ForeignKey, create_engine, Column, Table, select
# from sqlalchemy import create_engine, select
# from sqlalchemy.orm import sessionmaker
from database import Base
# from database import Base, User, Message, Chat, chat_user

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from functools import partial


# class Base(DeclarativeBase):
#     pass

# class Message(Base):
#     __tablename__ = "message"
#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     text: Mapped[str] = mapped_column()
#     user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
#     user: Mapped["User"] = relationship(back_populates="messages")
#     chat_id: Mapped[int] = mapped_column(ForeignKey("chat.id"))
#     chat: Mapped["Chat"] = relationship(back_populates="messages")

# class Chat(Base):
#     __tablename__ = "chat"
#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     name: Mapped[str] = mapped_column()
#     users: Mapped[list["User"]] = relationship(secondary="chat_user", back_populates="chats")
#     messages: Mapped[list["Message"]] = relationship(back_populates="chat")

# class User(Base):
#     __tablename__ = "user"
#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     name: Mapped[str] = mapped_column()
#     password: Mapped[str] = mapped_column()
#     chats: Mapped[list["Chat"]] = relationship(secondary="chat_user", back_populates="users")
#     messages: Mapped[list["Message"]] = relationship(back_populates="user")


# chat_user = Table(
#     "chat_user",
#     Base.metadata,
#     Column("user_id", ForeignKey("user.id"), primary_key=True),
#     Column("chat_id", ForeignKey("chat.id"), primary_key=True)
# )




# class ChildWindow(tkinter.Toplevel):  # <-- Это вспомогательное окно (Дочернее)
#     def __init__(self, parent):
#         super().__init__(parent)  # Тут нужно указать родителя

#         self.__configure_window()
#         self.__configure_widgets()
#         self.__pack_widgets()

#     def __configure_window(self):
#         self.title("Дочь")
#         # self.grab_set()  # <-- Взять всё внимание на себя!

#     def __configure_widgets(self):
#         pass

#     def __pack_widgets(self):
#         pass

class RegFrame(tkinter.ttk.Frame):
    def __init__(self, container, Session):
        super().__init__(container)
        self.container = container
        self.SALT = "5ge87"
        self.Session = Session


        self.u_name: tkinter.ttk.Label
        self.__main_label: tkinter.ttk.Label
        self.__desc_label: tkinter.ttk.Label
        self.__res: tkinter.ttk.Label
        self.__name_label: tkinter.ttk.Label
        self.__name_entry: tkinter.ttk.Entry
        self.__password_label: tkinter.ttk.Label
        self.__password_entry: tkinter.ttk.Entry
        self.__enter_button: tkinter.ttk.Button
        self.__reg_button: tkinter.ttk.Button

        self.__configure_widgets()
        self.__pack_widgets()

    def __configure_widgets(self):
        self.container.u_name = tkinter.ttk.Label(self.container, text="Ваше имя: ")
        self.__main_label = tkinter.ttk.Label(self, text="Войдите в систему")
        self.__desc_label = tkinter.ttk.Label(self, text='Для входа введите в поля свои имя и пароль и нажмите кнопку "Войти"\nДля регистрации введите в поля свои имя и пароль и нажмите кнопку "Зарегистрироваться"')
        self.__res = tkinter.ttk.Label(self, text="")
        self.__name_label = tkinter.ttk.Label(self, text="Имя пользователя")
        self.__name_entry = tkinter.ttk.Entry(self)
        self.__password_label = tkinter.ttk.Label(self, text="Пароль")
        self.__password_entry = tkinter.ttk.Entry(self, show="*")
        self.__enter_button = tkinter.ttk.Button(self, text="Войти", command=self.__enter)
        self.__reg_button = tkinter.ttk.Button(self, text="Зарегистрироваться", command=self.__reg)

    def __pack_widgets(self):
        self.container.u_name.pack()
        self.__main_label.pack(pady=10)
        self.__desc_label.pack(pady=(0, 5))

        self.__name_label.pack(pady=5)
        self.__name_entry.pack()
        self.__password_label.pack(pady=5)
        self.__password_entry.pack()
        self.__enter_button.pack(side=tkinter.LEFT, expand=True, pady=10)
        self.__reg_button.pack(side=tkinter.LEFT, expand=True, pady=10)


    def __reg(self):
        name = self.__name_entry.get()
        password = self.__password_entry.get()

        if name == "" or password == "":
            self.__res.pack_forget()
            self.__res = tkinter.ttk.Label(text="Введите имя и пароль")
            self.__res.pack(side=tkinter.BOTTOM)
            
        else:
            with self.Session() as session:
                stmt = select(User).where(User.name == name)
                users = session.scalars(stmt).all()
                if users == []:
                    hashed_password = hashlib.md5((password+self.SALT).encode()).hexdigest()
                    new_user = User(name = name, password = hashed_password)
                    session.add(new_user)
                    session.commit()
                    
                else:
                    self.__res.pack_forget()
                    self.__res = tkinter.ttk.Label(text="Это имя уже использовано")
                    self.__res.pack(side=tkinter.BOTTOM)

    def __enter(self):
        name = self.__name_entry.get()
        password = self.__password_entry.get()
        hashed_password = hashlib.md5((password+self.SALT).encode()).hexdigest()
        with self.Session() as session:
            stmt = select(User).where(name == User.name)
            user: User | None = session.scalars(stmt).first()
            if user is not None:
                if user.password == hashed_password:
                    self.__res.pack_forget()
                    self.pack_forget()
                    self.container.u_name['text'] += name
                    self.container.chats_frame.show(user.name)

                else:
                    self.__res.pack_forget()
                    self.__res = tkinter.ttk.Label(text="Введены неверные данные")
                    self.__res.pack(side=tkinter.BOTTOM)
            else:
                self.__res.pack_forget()
                self.__res = tkinter.ttk.Label(text="Пользователь с этим именем не существует\nЗарегистрируйтесь")
                self.__res.pack(side=tkinter.BOTTOM)

    def show(self):
        self.pack()





class ListChatsFrame(tkinter.ttk.Frame):
    def __init__(self, container, Session, username):
        super().__init__(container)
        self.container = container
        self.Session = Session
        self.buttons = []
        self.username = username
        
        self.__button: tkinter.ttk.Label

        self.__configure_widgets()

        

    def __configure_widgets(self):
        if self.username != "":

            with self.Session() as session:
                stmt = select(User).where(User.name == self.username)
                the_user: User | None = session.scalars(stmt).first()
                if the_user is not None:
                    for chat in the_user.chats:
                        self.__button = tkinter.ttk.Button(
                            self, 
                            text=chat.name, 
                            command=partial(self.open_chat, chat.id))
                        self.__button.pack(fill="both", expand=True)

    def open_chat(self, chat_id):
        self.pack_forget()
        self.container.pack_forget()
        self.container.container.chat_frame.show(self.username, chat_id)
        
    def show(self, username):
        self.username = username
        self.__configure_widgets()
        self.pack(fill="both", expand=True)





class ChatsFrame(tkinter.ttk.Frame):
    def __init__(self, container, Session):
        super().__init__(container)
        self.container = container
        self.username = ""
        self.Session = Session

        self.__main_label: tkinter.ttk.Label
        self.__desc_label: tkinter.ttk.Label
        self.__start_button: tkinter.ttk.Button

        self.canvas: tkinter.Canvas
        self.scrollbar: tkinter.Scrollbar 
        self.list_chats_frame: ListChatsFrame
        self.__configure_widgets()
        self.__pack_widgets()

    def __configure_widgets(self):
        self.__main_label = tkinter.ttk.Label(self, text="Все чаты")
        self.__desc_label = tkinter.ttk.Label(self, text="Начать чат с пользователем")
        self.__start_button = tkinter.ttk.Button(self, text="Найти пользователя", command=self.open_search)
        
        self.canvas = tkinter.Canvas(self) 
        self.scrollbar = tkinter.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set) 

        self.bind_all("<MouseWheel>", self._on_mousewheel)

        self.list_chats_frame = ListChatsFrame(self, self.Session, self.username)
        self.canvas.create_window((0, 0), window=self.list_chats_frame, anchor="nw")
        self.list_chats_frame.update_idletasks()  
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def __pack_widgets(self):
        self.__main_label.pack(pady=(5, 10))
        self.__desc_label.pack(pady=(0, 5))
        self.__start_button.pack()
        self.scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)  
        self.canvas.pack(fill=tkinter.BOTH, expand=True) 
        self.list_chats_frame.show(self.username)


    def open_search(self):
        self.pack_forget()
        self.container.find_user_frame.show(self.username)
        

    def show(self, username):
        self.username = username
        self.pack()
        self.list_chats_frame.show(self.username)





class FindUserFrame(tkinter.ttk.Frame):
    def __init__(self, container, Session):
        super().__init__(container)
        self.container = container

        self.username = ""
        self.all_user_start_buttons = []
        self.Session = Session


        self.__main_label: tkinter.ttk.Label
        self.__desc_label: tkinter.ttk.Label
        self.__entry: tkinter.ttk.Entry
        self.__search_button: tkinter.ttk.Button

        
        self.__user_button: tkinter.ttk.Button

        self.__exit_button: tkinter.ttk.Button


        self.__configure_widgets()
        self.__pack_widgets()

    def __configure_widgets(self):
        self.__main_label = tkinter.ttk.Label(self, text="Введите имя пользователя")
        self.__desc_label = tkinter.ttk.Label(self, text='Введите "*", чтобы увидеть всех пользователей')
        self.__entry = tkinter.ttk.Entry(self)
        self.__search_button = tkinter.ttk.Button(self, text="Найти пользователя", command=self.__find)
        self.__exit_button = tkinter.ttk.Button(self, text="Назад", command=self.__exit)

    def __pack_widgets(self):

        self.__main_label.pack(pady=(5, 10))
        self.__desc_label.pack(pady=(0, 5))
        self.__entry.pack()
        self.__search_button.pack(pady=3)
        self.__exit_button.pack(side=tkinter.BOTTOM)
        

    def __exit(self):
        self.__entry.delete(0, tkinter.END)
        self.pack_forget()
        self.container.chats_frame.show(self.username) 
    
    def __find(self):
        for el in self.all_user_start_buttons:
            el.pack_forget()
        with self.Session() as session:
            get_name = self.__entry.get()
            if get_name == "*":

                stmt = select(User).where(self.username != User.name)
                users: User | None = session.scalars(stmt).all()

            else:
                if self.username != self.__entry.get():
                    stmt = select(User).where(self.__entry.get() == User.name)
                    users: User | None = session.scalars(stmt).all()
                else:
                    users = None


            if users is not None:
                for user in users:
                    self.__user_button = tkinter.ttk.Button(
                        self, 
                        text=user.name, 
                        command=partial(self.start_chat, user.name))
                    self.__user_button.pack(pady=3, ipadx=3, ipady=3, expand=True, fill=tkinter.X)
                    self.all_user_start_buttons.append(self.__user_button)
            else:
                self.__user_button = tkinter.ttk.Button(self, text="Других пользователей не найдено", command=self.start_chat)
                self.__user_button.pack(pady=3, ipadx=3, ipady=3, expand=True, fill=tkinter.X)
                self.all_user_start_buttons.append(self.__user_button)
        


    def start_chat(self, sec_username):        
        self.__entry.delete(0, tkinter.END)
        self.__user_button.pack_forget()
        self.pack_forget()
        self.container.configure_chat_frame.show(self.username, sec_username)
        

    def show(self, username):
        self.username = username
        self.pack()





class ConfigureChatFrame(tkinter.ttk.Frame):
    def __init__(self, container, Session):
        super().__init__(container)
        self.container = container
        self.username = ""
        self.Session = Session
        self.username = ""
        self.sec_username = ""

        self.__main_label: tkinter.ttk.Label
        self.__name_label: tkinter.ttk.Label
        self.__name_entry: tkinter.ttk.Entry
        self.__save_button: tkinter.ttk.Button
        self.__exit_button: tkinter.ttk.Button

        self.__configure_widgets()
        self.__pack_widgets()

    def __configure_widgets(self):
        self.__main_label = tkinter.ttk.Label(self, text="Создание чата")
        self.__name_label = tkinter.ttk.Label(self, text="Введите название чата")
        self.__name_entry = tkinter.ttk.Entry(self)
        self.__save_button = tkinter.ttk.Button(self, text="Создать чат", command=self.__create_chat)
        self.__exit_button = tkinter.ttk.Button(self, text="Назад", command=self.__exit)

    def __pack_widgets(self):
        self.__main_label.pack(pady=(5, 10))
        self.__name_label.pack(pady=(0, 5))
        self.__name_entry.pack()
        self.__save_button.pack(pady=3)
        self.__exit_button.pack()

    def __exit(self):
        self.__name_entry.delete(0, tkinter.END)
        
        self.pack_forget()
        self.container.chats_frame.show(self.username)


    def __create_chat(self):
        with self.Session() as session:
            name = self.__name_entry.get()
            self.__name_entry.delete(0, tkinter.END)
            users = []

            stmt = select(User).where(User.name==self.sec_username)
            sec_user = session.scalars(stmt).first()
            username = self.container.u_name['text'][10:]

            stmt = select(User).where(User.name==username)
            user = session.scalars(stmt).first()

            if user != None and sec_user != None:
                new_chat = Chat(name=name, users=users)
                session.add(new_chat)
                session.commit()

                user.chats.append(new_chat)
                sec_user.chats.append(new_chat)

                new_chat.users.append(user)
                new_chat.users.append(sec_user)

                    


                session.commit()
                self.pack_forget()
                self.container.chats_frame.show(self.username)



    def show(self, username, sec_username):
        self.sec_username = sec_username
        self.username = username
        self.pack()




class ChatFrame(tkinter.ttk.Frame):
    def __init__(self, container, Session):
        super().__init__(container)
        self.container = container
        self.chat_id = 0
        self.username = ""
        self.Session = Session

        self.__chat_label: tkinter.ttk.Label
        self.__messages_frame: MessagesFrame
        
        self.__entry: tkinter.ttk.Entry
        self.__send_button: tkinter.ttk.Button

        self.__configure_widgets()
        self.__pack_widgets()

    def __configure_widgets(self):
        self.__chat_label = tkinter.ttk.Label(self, text="")
        self.__entry = tkinter.ttk.Entry(self)
        self.__send_button = tkinter.ttk.Button(self, text=">", command=self.__send_message)
        with self.Session() as session:
            stmt = select(Chat).where(Chat.id == self.chat_id)
            chat: Chat | None = session.scalars(stmt).first()
            if chat is not None:
                self.__messages_frame = MessagesFrame(self, self.Session)
                self.__messages_frame.show(self.username, self.chat_id)
                self.__chat_label = tkinter.ttk.Label(self, text=chat.name)



    def __pack_widgets(self):
        self.__chat_label.pack(pady=(5, 10))

        self.__entry.pack(pady=5, side=tkinter.LEFT)
        self.__send_button.pack(pady=5, side=tkinter.LEFT)

    def __send_message(self):
        text = self.__entry.get()
        user = self.username
        chat_id = self.chat_id
        with self.Session() as session:
            stmt = select(Chat).where(Chat.id == self.chat_id)
            chat: Chat | None = session.scalars(stmt).first()

            for u in chat.users:
                if u.name == user:
                    user = u
                    
            if chat is not None:
                message = Message(text=text, user=user, user_id=user.id, chat_id=chat_id, chat=chat)
                session.add(message)
                session.commit()
                chat.messages.append(message)
                session.commit()

    def show(self, username, chat_id):
            self.username = username
            self.chat_id = chat_id
            self.pack()




class MessagesFrame(tkinter.ttk.Frame):
    def __init__(self, container, Session):
        super().__init__(container)
        self.container = container
        self.chat_id = 0
        self.username = ""
        self.Session = Session
        r = 0

        self.__username_label: tkinter.ttk.Label
        self.__message_label: tkinter.ttk.Label

        self.__configure_widgets()
        self.__pack_widgets()

    def __configure_widgets(self):
        with self.Session() as session:
            stmt = select(Chat).where(Chat.id == self.chat_id)
            chat = session.scalars(stmt).first()
            for m in chat.messages:
                if m.user.name == self.username:
                    self.__username_label = tkinter.ttk.Label(self, text=m.user.name)
                    self.__message_label = tkinter.ttk.Label(self, text=m.text)
                    self.__username_label.grid(row=r, colunm=2)
                    r += 1
                    self.__message_label.grid(row=r, colunm=2)
                    r += 1
                elif m.user.name in chat.users:
                    self.__username_label = tkinter.ttk.Label(self, text=m.user.name)
                    self.__message_label = tkinter.ttk.Label(self, text=m.text)
                    self.__username_label.grid(row=r, colunm=1)
                    r += 1
                    self.__message_label.grid(row=r, colunm=1)
                    r += 1


    def show(self, username, chat_id):
        self.username = username
        self.chat_id = chat_id
        self.pack(expand=True, fill=tkinter.BOTH)




class App(tkinter.Tk):
    def __init__(self, Session):
        super().__init__()

        self.Session = Session


        # self.__child_windows: list = [] #дети

        # self.__chat_buttons: list = [] #кнопкu для открытия дочернего окна

        self.reg_frame: RegFrame
        self.chats_frame: ChatsFrame
        self.find_user_frame: FindUserFrame
        self.configure_chat_frame: ConfigureChatFrame
        self.chat_frame: ChatFrame

        self.__configure_window()
        self.__configure_widgets()
        self.__pack_widgets()

    def __configure_window(self):
        self.title("Мессенджер")
        self.geometry("700x280")

    def __configure_widgets(self):
        
        self.reg_frame = RegFrame(self, self.Session)
        self.chats_frame = ChatsFrame(self, self.Session)
        self.find_user_frame = FindUserFrame(self, self.Session)
        self.configure_chat_frame = ConfigureChatFrame(self, self.Session)
        self.chat_frame = ChatFrame(self, self.Session)

        # #настройка кнопки для открытия дочернего окна
        # self.__chat_button = tkinter.ttk.Button( 
        #     self, text="Создать дочернее окно", command=self.__open_child_window
        # )





    def __pack_widgets(self):
        self.reg_frame.show()

















    # def __open_child_window(self):
    #     # 1. Создание дочернего окна
    #     self.__child_windows.append(ChildWindow(self))

    #     # self.wait_window(self.__child_windows[-1])
    #     # Код ниже в методе работать не будет
    #     # пока открыто окно, которое ждём

    #     # 2. Проверка того, что родитель ещё работает!
    #     print("Родитель на работе! (Работает)")
        
    


    def run(self):
        self.mainloop()


# def main():
    
#     engine = create_engine("sqlite:///messenger.db")
#     Base.metadata.create_all(bind=engine)
#     Session = sessionmaker(bind=engine)


    


if __name__ == "__main__":
    engine = create_engine("sqlite:///messenger.db")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    app = App(Session)
    app.run()
    