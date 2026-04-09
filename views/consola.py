import os
from datetime import date


# ── Terminal helpers ───────────────────────────

def limpiar():
    os.system("cls" if os.name == "nt" else "clear")


def pausar():
    input("\n  Presiona Enter para continuar...")


def encabezado(titulo: str):
    print("\n" + "═" * 50)
    print(f"  {titulo}")
    print("═" * 50)


# ── Formateo ───────────────────────────────────

def fmt_hora(h: int) -> str:
    return f"{h:02d}:00 - {h+1:02d}:00"


def fmt_estado(estado: str) -> str:
    iconos = {"pendiente": "⏳", "aprobada": "✅", "cancelada": "❌"}
    return f"{iconos.get(estado, '?')} {estado}"


def fmt_dia(fecha_iso: str) -> str:
    return date.fromisoformat(fecha_iso).strftime("%A")


# ── Menús ──────────────────────────────────────

def menu_principal():
    limpiar()
    encabezado("CANCHA UNIDAD RESIDENCIAL")
    print("  Horario: 06:00 — 22:00  |  Bloques de 1 hora\n")
    print("  [1] Ver horarios disponibles")
    print("  [2] Hacer una reserva")
    print("  [3] Ver mis reservas")
    print("  [4] Actualizar una reserva")
    print("  [5] Eliminar una reserva")
    print("  [6] Panel administrador")
    print("  [0] Salir")
    return input("\n  Opción: ").strip()


def menu_admin():
    limpiar()
    encabezado("PANEL ADMINISTRADOR")
    print("  [1] Ver todas las reservas")
    print("  [2] Aprobar reserva")
    print("  [3] Cancelar reserva")
    print("  [4] Eliminar reserva")
    print("  [0] Salir del panel")
    return input("\n  Opción: ").strip()


# ── Inputs ─────────────────────────────────────

def pedir_apartamento() -> str:
    return input("  Número de apartamento: ").strip()


def pedir_pin() -> str:
    return input("  PIN de administrador: ").strip()


def pedir_id(accion="") -> str:
    return input(f"  ID de la reserva{' a ' + accion if accion else ''}: ").strip()


def pedir_confirmacion(mensaje="¿Confirmar?") -> bool:
    return input(f"  {mensaje} (s/n): ").strip().lower() == "s"


def seleccionar_de_lista(items: list, etiqueta: str) -> int | None:
    """Muestra una lista numerada y retorna el índice 0-based, o None si cancela."""
    for i, item in enumerate(items):
        print(f"  [{i+1}] {item}")
    op = input(f"\n  {etiqueta}: ").strip()
    if op.isdigit() and 1 <= int(op) <= len(items):
        return int(op) - 1
    return None


# ── Pantallas de visualización ─────────────────

def mostrar_dias(dias: list):
    print("\n  Selecciona un día:")
    opciones = [f"{d}  ({fmt_dia(d)})" for d in dias]
    return opciones


def mostrar_horarios_dia(fecha: str, reservados: dict, horarios: list):
    limpiar()
    encabezado(f"HORARIOS — {fecha}")
    print(f"  {'Hora':<18} {'Estado':<16} {'Apartamento'}")
    print("  " + "-" * 46)
    for h in horarios:
        if h in reservados:
            r = reservados[h]
            print(f"  {fmt_hora(h):<18} {fmt_estado(r['estado']):<16} Apto {r['apartamento']}")
        else:
            print(f"  {fmt_hora(h):<18} 🟢 Disponible")


def mostrar_mis_reservas(apartamento: str, rows: list):
    limpiar()
    encabezado(f"RESERVAS — APTO {apartamento}")
    if not rows:
        print("  No hay reservas para ese apartamento.")
        return
    print(f"  {'ID':<6} {'Fecha':<12} {'Hora':<18} {'Estado'}")
    print("  " + "-" * 52)
    for r in rows:
        print(f"  {r[0]:<6} {r[1]:<12} {fmt_hora(r[2]):<18} {fmt_estado(r[3])}")


def mostrar_todas_reservas(rows: list):
    limpiar()
    encabezado("TODAS LAS RESERVAS")
    if not rows:
        print("  No hay reservas registradas.")
        return
    print(f"  {'ID':<6} {'Apto':<8} {'Fecha':<12} {'Hora':<18} {'Estado'}")
    print("  " + "-" * 58)
    for r in rows:
        print(f"  {r[0]:<6} {r[1]:<8} {r[2]:<12} {fmt_hora(r[3]):<18} {fmt_estado(r[4])}")


def mostrar_detalle_reserva(reserva: tuple):
    print(f"\n  ID: {reserva[0]}  |  Apto: {reserva[1]}  |  {reserva[2]}  |  "
          f"{fmt_hora(reserva[3])}  |  {fmt_estado(reserva[4])}")


# ── Mensajes de resultado ──────────────────────

def ok(msg: str):
    print(f"\n  ✅ {msg}")


def error(msg: str):
    print(f"\n  ❌ {msg}")
