
import flask
from sqlalchemy import create_engine#, select
from database import Base#, chat_user, User, Message, Chat, 

from sqlalchemy.orm import sessionmaker
from gui import App


flask_app = flask.Flask(__name__)

@flask_app.route("/")
def start():
    engine = create_engine("sqlite:///messenger.db")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)

    tkinter_app = App(Session)
    tkinter_app.run()
    return tkinter_app



if __name__ == "__main__":
    flask_app.run(debug=True)