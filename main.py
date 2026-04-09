from models.reserva import init_db
from gui import ReservaApp


def main():
    init_db()
    app = ReservaApp()
    app.mainloop()


if __name__ == "__main__":
    main()
