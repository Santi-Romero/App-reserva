from models.reserva import init_db
from views import consola as view
from controllers import reserva_controller as ctrl
from controllers import admin_controller as admin

ACCIONES = {
    "1": ctrl.ver_horarios,
    "2": ctrl.nueva_reserva,
    "3": ctrl.mis_reservas,
    "4": ctrl.actualizar_reserva,
    "5": ctrl.eliminar_reserva,
    "6": admin.panel_admin,
}


def main():
    init_db()
    while True:
        op = view.menu_principal()
        if op == "0":
            view.limpiar()
            print("  Hasta luego!\n")
            break
        accion = ACCIONES.get(op)
        if accion:
            accion()
        else:
            view.error("Opción inválida.")
            view.pausar()


if __name__ == "__main__":
    main()
