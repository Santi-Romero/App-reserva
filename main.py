from models.reserva import init_db
from gui import LoginWindow


def main():
    init_db()
    app = LoginWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
