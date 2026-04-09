import sqlite3
from datetime import datetime
from models import reserva as model
from views import consola as view


def ver_horarios():
    dias = model.proximos_dias()
    view.limpiar()
    view.encabezado("VER HORARIOS DISPONIBLES")
    opciones = view.mostrar_dias(dias)
    idx = view.seleccionar_de_lista(opciones, "Día")
    if idx is None:
        return

    fecha = dias[idx]
    reservados = model.reservas_por_fecha(fecha)
    view.mostrar_horarios_dia(fecha, reservados, model.HORARIOS)
    view.pausar()


def nueva_reserva():
    view.limpiar()
    view.encabezado("NUEVA RESERVA")

    apartamento = view.pedir_apartamento()
    if not apartamento:
        view.error("Apartamento requerido.")
        view.pausar()
        return

    dias = model.proximos_dias()
    view.limpiar()
    view.encabezado("NUEVA RESERVA")
    print(f"\n  Apartamento: {apartamento}")
    print("\n  Selecciona el día:")
    opciones_dias = view.mostrar_dias(dias)
    idx_dia = view.seleccionar_de_lista(opciones_dias, "Día")
    if idx_dia is None:
        view.error("Opción inválida.")
        view.pausar()
        return
    fecha = dias[idx_dia]

    disponibles = model.horarios_disponibles(fecha)
    if not disponibles:
        view.error("No hay horarios disponibles ese día.")
        view.pausar()
        return

    view.limpiar()
    view.encabezado("NUEVA RESERVA")
    print(f"\n  Apartamento: {apartamento}  |  Fecha: {fecha}")
    print(f"\n  Horarios disponibles:")
    opciones_hora = [view.fmt_hora(h) for h in disponibles]
    idx_hora = view.seleccionar_de_lista(opciones_hora, "Hora")
    if idx_hora is None:
        view.error("Opción inválida.")
        view.pausar()
        return
    hora = disponibles[idx_hora]

    try:
        model.insertar_reserva(apartamento, fecha, hora, datetime.now().isoformat())
        view.ok("Reserva creada. Estado: pendiente (espera aprobación del admin).")
    except sqlite3.IntegrityError:
        view.error("Ese horario ya está reservado.")
    view.pausar()


def mis_reservas():
    view.limpiar()
    view.encabezado("MIS RESERVAS")
    apartamento = view.pedir_apartamento()
    if not apartamento:
        view.pausar()
        return
    rows = model.reservas_por_apartamento(apartamento)
    view.mostrar_mis_reservas(apartamento, rows)
    view.pausar()


def actualizar_reserva():
    view.limpiar()
    view.encabezado("ACTUALIZAR RESERVA")
    rid = view.pedir_id("modificar")
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

    dias = model.proximos_dias()
    print("\n  Nuevo día:")
    opciones_dias = view.mostrar_dias(dias)
    idx_dia = view.seleccionar_de_lista(opciones_dias, "Día")
    if idx_dia is None:
        view.error("Opción inválida.")
        view.pausar()
        return
    nueva_fecha = dias[idx_dia]

    # Si es el mismo día, excluir el bloque actual para que aparezca disponible
    excluir = reserva[3] if nueva_fecha == reserva[2] else None
    disponibles = model.horarios_disponibles(nueva_fecha, excluir_hora=excluir)

    print(f"\n  Horarios disponibles el {nueva_fecha}:")
    opciones_hora = [view.fmt_hora(h) for h in disponibles]
    idx_hora = view.seleccionar_de_lista(opciones_hora, "Hora")
    if idx_hora is None:
        view.error("Opción inválida.")
        view.pausar()
        return
    nueva_hora = disponibles[idx_hora]

    try:
        model.mover_reserva(int(rid), nueva_fecha, nueva_hora)
        view.ok("Reserva actualizada. Estado vuelve a: pendiente.")
    except sqlite3.IntegrityError:
        view.error("Ese horario ya está ocupado.")
    view.pausar()


def eliminar_reserva():
    view.limpiar()
    view.encabezado("ELIMINAR RESERVA")
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
    if view.pedir_confirmacion("¿Eliminar esta reserva?"):
        model.borrar_reserva(int(rid))
        view.ok("Reserva eliminada.")
    else:
        print("  Operación cancelada.")
    view.pausar()
