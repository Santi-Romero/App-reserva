from models import reserva as model
from views import consola as view


def panel_admin():
    view.limpiar()
    view.encabezado("PANEL ADMINISTRADOR")
    if view.pedir_pin() != model.ADMIN_PIN:
        view.error("PIN incorrecto.")
        view.pausar()
        return

    acciones = {
        "1": _ver_todas,
        "2": _aprobar,
        "3": _cancelar,
        "4": _eliminar,
    }

    while True:
        op = view.menu_admin()
        if op == "0":
            break
        accion = acciones.get(op)
        if accion:
            accion()
        else:
            view.error("Opción inválida.")
            view.pausar()


# ── Acciones privadas ──────────────────────────

def _ver_todas():
    rows = model.todas_las_reservas()
    view.mostrar_todas_reservas(rows)
    view.pausar()


def _aprobar():
    rows = model.todas_las_reservas(solo_pendientes=True)
    view.limpiar()
    view.encabezado("APROBAR RESERVA")
    if not rows:
        view.error("No hay reservas pendientes.")
        view.pausar()
        return

    view.mostrar_todas_reservas(rows)
    rid = view.pedir_id("aprobar")
    if not rid.isdigit():
        view.error("ID inválido.")
        view.pausar()
        return

    reserva = model.buscar_por_id(int(rid))
    if not reserva or reserva[4] != "pendiente":
        view.error("Reserva no encontrada o ya procesada.")
        view.pausar()
        return

    model.set_estado(int(rid), "aprobada")
    view.ok("Reserva aprobada.")
    view.pausar()


def _cancelar():
    view.limpiar()
    view.encabezado("CANCELAR RESERVA")
    rid = view.pedir_id("cancelar")
    if not rid.isdigit():
        view.error("ID inválido.")
        view.pausar()
        return

    reserva = model.buscar_por_id(int(rid))
    if not reserva:
        view.error("Reserva no encontrada.")
        view.pausar()
        return

    view.mostrar_detalle_reserva(reserva)
    if view.pedir_confirmacion("¿Cancelar esta reserva?"):
        model.set_estado(int(rid), "cancelada")
        view.ok("Reserva cancelada.")
    else:
        print("  Operación cancelada.")
    view.pausar()


def _eliminar():
    view.limpiar()
    view.encabezado("ELIMINAR RESERVA (ADMIN)")
    rid = view.pedir_id("eliminar")
    if not rid.isdigit():
        view.error("ID inválido.")
        view.pausar()
        return

    reserva = model.buscar_por_id(int(rid))
    if not reserva:
        view.error("Reserva no encontrada.")
        view.pausar()
        return

    view.mostrar_detalle_reserva(reserva)
    if view.pedir_confirmacion("¿Eliminar permanentemente?"):
        model.borrar_reserva(int(rid))
        view.ok("Reserva eliminada.")
    else:
        print("  Operación cancelada.")
    view.pausar()
