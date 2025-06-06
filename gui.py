
import tkinter
from tkinter import font
import tkinter.ttk
from database import User, Message, Chat#, Base, chat_user
from sqlalchemy import select#create_engine
import hashlib
from functools import partial
from tkinter import Canvas, Frame, Scrollbar, VERTICAL, NW
from time import sleep

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
        self.__main_label = tkinter.ttk.Label(self, text="Войдите в систему", style="Main.TLabel")
        self.__desc_label = tkinter.ttk.Label(self, text='Для входа введите в поля свои имя и пароль и нажмите кнопку "Войти"\nДля регистрации введите в поля свои имя и пароль и нажмите кнопку "Зарегистрироваться"')
        self.__res = tkinter.ttk.Label(self, text="")
        self.__name_label = tkinter.ttk.Label(self, text="Имя пользователя")
        self.__name_entry = tkinter.ttk.Entry(self, font=font.Font(size=14))
        
        self.__password_label = tkinter.ttk.Label(self, text="Пароль")
        self.__password_entry = tkinter.ttk.Entry(self, show="*", font=font.Font(size=14))
        self.__enter_button = tkinter.ttk.Button(self, text="Войти", command=self.__enter)
        self.__reg_button = tkinter.ttk.Button(self, text="Зарегистрироваться", command=self.__reg)


    def __pack_widgets(self):
        self.container.u_name.pack()
        self.__main_label.pack(pady=10)
        self.__desc_label.pack(pady=(0, 5))

        self.__name_label.pack(pady=5)
        self.__name_entry.pack()
        self.__name_entry.focus_set()
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
        self.canvas = Canvas(self)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar = Scrollbar(self, orient=VERTICAL, command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.inner_frame = Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor=NW)

        self.inner_frame.bind_all("<MouseWheel>", self._on_mousewheel)
        self.inner_frame.bind("<Configure>", lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
    
    


        if self.username != "":

            with self.Session() as session:
                stmt = select(User).where(User.name == self.username)
                the_user: User | None = session.scalars(stmt).first()
                if the_user is not None:
                    for chat in the_user.chats:
                        self.__button = tkinter.ttk.Button(
                            self.inner_frame, 
                            text=chat.name, 
                            command=partial(self.open_chat, chat.id))
                        self.__button.pack(fill=tkinter.X, expand=True)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")



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

        self.list_chats_frame: ListChatsFrame
        self.__configure_widgets()
        self.__pack_widgets()

    def __configure_widgets(self):
        self.__main_label = tkinter.ttk.Label(self, text="Все чаты", style="Main.TLabel")
        self.__desc_label = tkinter.ttk.Label(self, text="Начать чат с пользователем")
        self.__start_button = tkinter.ttk.Button(self, text="Найти пользователя", command=self.open_search)

        self.list_chats_frame = ListChatsFrame(self, self.Session, self.username)


    def __pack_widgets(self):
        self.__main_label.pack(pady=(5, 10))
        self.__desc_label.pack(pady=(0, 5))
        self.__start_button.pack(pady=(0, 10))

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
        self.__main_label = tkinter.ttk.Label(self, text="Поиск собеседника", style="Main.TLabel")
        self.__desc_label = tkinter.ttk.Label(self, text='Введите имя пользователя\nВведите "*", чтобы увидеть всех пользователей')
        self.__entry = tkinter.ttk.Entry(self, font=font.Font(size=14))
        
        self.__search_button = tkinter.ttk.Button(self, text="Найти пользователя", command=self.__find)
        self.__exit_button = tkinter.ttk.Button(self, text="Назад", command=self.__exit)

    def __pack_widgets(self):

        self.__main_label.pack(pady=(5, 10))
        self.__desc_label.pack(pady=(0, 5))
        self.__entry.pack(pady=5)
        self.__entry.focus_set()
        self.__search_button.pack(pady=3)
        self.__exit_button.pack(side=tkinter.BOTTOM, pady=5)
        

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
        self.__main_label = tkinter.ttk.Label(self, text="Создание чата", style="Main.TLabel")
        self.__name_label = tkinter.ttk.Label(self, text="Введите название чата")
        self.__name_entry = tkinter.ttk.Entry(self, font=font.Font(size=14))
        
        self.__save_button = tkinter.ttk.Button(self, text="Создать чат", command=self.__create_chat)
        self.__exit_button = tkinter.ttk.Button(self, text="Назад", command=self.__exit)

    def __pack_widgets(self):
        self.__main_label.pack(pady=(5, 10))
        self.__name_label.pack(pady=(0, 5))
        self.__name_entry.pack(padx=7)
        self.__name_entry.focus_set()
        self.__save_button.pack(pady=5)
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
        self.pack(expand=True, fill=tkinter.BOTH)










class ChatFrame(tkinter.ttk.Frame):
    def __init__(self, container, Session):
        super().__init__(container)
        self.container = container
        self.chat_id = "="
        self.username = ""
        self.Session = Session

        self.__chat_label: tkinter.ttk.Label
        self.__user_label: tkinter.ttk.Label
        self.__messages_frame: MessagesFrame
        self.canvas: tkinter.Canvas 
        self.scrollbar: tkinter.Scrollbar

        
        self.__entry_frame: tkinter.ttk.Frame
        self.__entry: tkinter.ttk.Entry
        self.__send_button: tkinter.ttk.Button
        self.__exit_button: tkinter.ttk.Button

        self.__configure_widgets()


    def __configure_widgets(self):

        self.__chat_label = tkinter.ttk.Label(self, text="", style="Main.TLabel")
        self.__entry_frame = tkinter.ttk.Frame(self)
        self.__entry = tkinter.ttk.Entry(self.__entry_frame, font=font.Font(size=14))
        
        self.__send_button = tkinter.ttk.Button(self.__entry_frame, text=">", command=self.__send_message)
        self.__exit_button = tkinter.ttk.Button(self, text="Назад", command=self.__exit)

        self.bind("<KeyPress-Return>", self.__send_message)

    def __update_chat(self):
        self.__entry.delete(0, tkinter.END)
        self.__exit_button.pack_forget()
        self.__entry_frame.pack_forget()

        with self.Session() as session:
            stmt = select(Chat).where(Chat.id == self.chat_id)
            chat: Chat | None = session.scalars(stmt).first()
            if chat is not None:
                for u in chat.users:
                    if u.name != self.username:
                        self.__user_label = tkinter.ttk.Label(self, text=u.name)

                self.__messages_frame = MessagesFrame(self, self.Session)
                self.__chat_label = tkinter.ttk.Label(self, text=chat.name)
        self.__pack_widgets()
        

    def __pack_widgets(self):
        self.__chat_label.pack(pady=(5, 10))
        self.__user_label.pack()
        self.__messages_frame.show(self.username, self.chat_id)
        self.__exit_button.pack(pady=5, side=tkinter.BOTTOM)

        self.__entry_frame.pack(side=tkinter.BOTTOM)
        self.__entry.pack(pady=5, padx=5, side=tkinter.LEFT)
        self.__entry.focus_set()
        self.__send_button.pack(pady=5, side=tkinter.LEFT)

    def __close(self):
        self.__user_label.pack_forget()
        self.__chat_label.pack_forget()
        self.__messages_frame.pack_forget()


    def __exit(self):
        self.__close()
        self.pack_forget()
        self.container.in_chat = False
        self.container.chats_frame.show(self.username) 

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
                chat.messages.append(message)
                session.commit()
                stmt = select(Message).where(Message.id == message.id)
                message: Message | None = session.scalars(stmt).first()
                
        self.__close()
        self.__update_chat()


    def show(self, username, chat_id):
        self.username = username
        self.chat_id = chat_id
        self.__update_chat()
        self.pack()
        self.container.in_chat = True
        # while self.container
        # with self.Session() as session:
        #     stmt = select(Chat).where(Chat.id == self.chat_id)
        #     chat: Message | None = session.scalars(stmt).first()
        #     sleep(2)
        #     stmt = select(Chat).where(Chat.id == self.chat_id)
        #     chat2: Message | None = session.scalars(stmt).first()
        #     while len(chat.messages) == len(chat2.messages):
        #         stmt = select(Chat).where(Chat.id == self.chat_id)
        #         chat: Message | None = session.scalars(stmt).first()
        #         sleep(2)
        #         stmt = select(Chat).where(Chat.id == self.chat_id)
        #         chat2: Message | None = session.scalars(stmt).first()
        #     self.__update_chat()



class ScrollableFrame(Frame):
    def __init__(self, master, **kwargs):
        Frame.__init__(self, master, **kwargs)

        self.canvas = Canvas(self)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = Scrollbar(self, orient=VERTICAL, command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.inner_frame = Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor=NW)
        

        self.inner_frame.bind_all("<MouseWheel>", self._on_mousewheel)
        self.inner_frame.bind("<Configure>", lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")), self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")



class MessagesFrame(tkinter.ttk.Frame):
    def __init__(self, container, Session):
        super().__init__(container)
        self.container = container
        self.chat_id = 0
        self.username = ""
        self.Session = Session
        self.r = 0


        self.labels = []
        self.messages = []


        self.__username_label: tkinter.ttk.Label
        self.__message_label: tkinter.ttk.Label
        self.frame: ScrollableFrame

    def __configure_widgets(self):

        self.frame = ScrollableFrame(self)
        self.frame.pack(fill="both", expand=True)

        with self.Session() as session:
            stmt = select(Chat).where(Chat.id == self.chat_id)
            chat = session.scalars(stmt).first()
            me_user: User
            second_user: User

            if chat is not None:
                for u in chat.users:
                    if u.name == self.username:
                        me_user = u
                    elif u.name != self.username:
                        second_user = u

                for m in chat.messages:
                    if m.user.name == me_user.name:
                        self.__username_label = tkinter.ttk.Label(self.frame.inner_frame, text=m.user.name+":")
                        self.__message_label = tkinter.ttk.Label(self.frame.inner_frame, text=m.text)
                        self.__username_label.grid(row=self.r, column=2)
                        self.r += 1
                        self.__message_label.grid(row=self.r, column=2)
                        self.r += 1
                        self.labels.append(self.__username_label)
                        self.messages.append(self.__message_label)

                    elif m.user.name == second_user.name:
                        self.__username_label = tkinter.ttk.Label(self.frame.inner_frame, text=m.user.name+":")
                        self.__message_label = tkinter.ttk.Label(self.frame.inner_frame, text=m.text, style="MessageText.TLabel")
                        self.__username_label.grid(row=self.r, column=1)
                        self.r += 1
                        self.__message_label.grid(row=self.r, column=1)
                        self.r += 1
                        self.labels.append(self.__username_label)
                        self.messages.append(self.__message_label)
    


    def show(self, username, chat_id):
        self.username = username
        self.chat_id = chat_id
        self.pack(expand=True, fill="both")
        self.__configure_widgets()


class App(tkinter.Tk):
    def __init__(self, Session):
        super().__init__()

        self.in_chat = False


        self.Session = Session

        self.reg_frame: RegFrame
        self.chats_frame: ChatsFrame
        self.find_user_frame: FindUserFrame
        self.configure_chat_frame: ConfigureChatFrame
        self.chat_frame: ChatFrame
        self.style: tkinter.ttk.Style

        self.__configure_window()
        self.__configure_widgets()
        self.__pack_widgets()

    def __configure_window(self):
        self.title("Мессенджер")
        self.geometry("830x480")

    def __configure_widgets(self):

        self.style = tkinter.ttk.Style()

        self.style.configure(
            "TLabel",
            font=("Arial", 14)
        )

        self.style.configure(
            "MessageText.TLabel",
            font=("Arial", 16)
        )
        
        self.style.configure(
            "Main.TLabel",
            font=("Arial", 20)
        )

        self.style.configure(
            "TButton",
            font=("Arial", 14)
        )

        self.style.configure(
            "TEntry",
            font=("Arial", 14),
            height=20
        )
        
        self.reg_frame = RegFrame(self, self.Session)
        self.chats_frame = ChatsFrame(self, self.Session)
        self.find_user_frame = FindUserFrame(self, self.Session)
        self.configure_chat_frame = ConfigureChatFrame(self, self.Session)
        self.chat_frame = ChatFrame(self, self.Session)

    def __pack_widgets(self):
        self.reg_frame.show()

    def run(self):
        self.mainloop()
    