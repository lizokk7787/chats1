import requests
from gui import App as app

url = "http://127.0.0.1:5000"


def main():

    app = requests.get(url+"/")


if __name__ == "__main__":
    main()