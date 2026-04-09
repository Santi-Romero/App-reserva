import sqlite3
import os
from datetime import datetime, date, timedelta

DB_FILE = "cancha.db"
HORARIOS = list(range(6, 22))  # 6am a 9pm (inicio de bloque)
DIAS_ANTICIPACION = 7

# ──────────────────────────────────────────────
# BASE DE DATOS
# ──────────────────────────────────────────────

def get_conn():
    return sqlite3.connect(DB_FILE)

def init_db():
    with get_conn() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS reservas (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                apartamento TEXT    NOT NULL,
                fecha       TEXT    NOT NULL,
                hora        INTEGER NOT NULL,
                estado      TEXT    NOT NULL DEFAULT 'pendiente',
                creada_en   TEXT    NOT NULL,
                UNIQUE(fecha, hora)
            )
        """)

# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────

def limpiar():
    os.system("cls" if os.name == "nt" else "clear")

def pausar():
    input("\n  Presiona Enter para continuar...")

def encabezado(titulo):
    print("\n" + "═" * 50)
    print(f"  {titulo}")
    print("═" * 50)

def formato_hora(h):
    return f"{h:02d}:00 - {h+1:02d}:00"

def estado_color(estado):
    colores = {"pendiente": "⏳", "aprobada": "✅", "cancelada": "❌"}
    return colores.get(estado, "?")

def proximos_dias():
    hoy = date.today()
    return [(hoy + timedelta(days=i)).isoformat() for i in range(DIAS_ANTICIPACION)]

# ──────────────────────────────────────────────
# OPERACIONES
# ──────────────────────────────────────────────

def obtener_reservas_fecha(fecha):
    with get_conn() as con:
        cur = con.execute(
            "SELECT hora, apartamento, estado FROM reservas WHERE fecha=? ORDER BY hora",
            (fecha,)
        )
        return {row[0]: {"apartamento": row[1], "estado": row[2]} for row in cur}

def crear_reserva(apartamento, fecha, hora):
    try:
        with get_conn() as con:
            con.execute(
                "INSERT INTO reservas (apartamento, fecha, hora, estado, creada_en) VALUES (?,?,?,?,?)",
                (apartamento, fecha, hora, "pendiente", datetime.now().isoformat())
            )
        return True, "Reserva creada. Estado: pendiente (espera aprobación del admin)."
    except sqlite3.IntegrityError:
        return False, "Ese horario ya está reservado."

def obtener_todas_reservas(solo_pendientes=False):
    with get_conn() as con:
        query = "SELECT id, apartamento, fecha, hora, estado FROM reservas"
        if solo_pendientes:
            query += " WHERE estado='pendiente'"
        query += " ORDER BY fecha, hora"
        return con.execute(query).fetchall()

def obtener_reserva_por_id(rid):
    with get_conn() as con:
        cur = con.execute(
            "SELECT id, apartamento, fecha, hora, estado FROM reservas WHERE id=?", (rid,)
        )
        return cur.fetchone()

def actualizar_reserva(rid, nueva_fecha, nueva_hora):
    try:
        with get_conn() as con:
            con.execute(
                "UPDATE reservas SET fecha=?, hora=?, estado='pendiente' WHERE id=?",
                (nueva_fecha, nueva_hora, rid)
            )
        return True, "Reserva actualizada. Estado vuelve a: pendiente."
    except sqlite3.IntegrityError:
        return False, "Ese horario ya está ocupado."

def eliminar_reserva(rid):
    with get_conn() as con:
        con.execute("DELETE FROM reservas WHERE id=?", (rid,))

def cambiar_estado(rid, nuevo_estado):
    with get_conn() as con:
        con.execute("UPDATE reservas SET estado=? WHERE id=?", (nuevo_estado, rid))

# ──────────────────────────────────────────────
# PANTALLAS
# ──────────────────────────────────────────────

def ver_horarios():
    limpiar()
    encabezado("VER HORARIOS DISPONIBLES")
    dias = proximos_dias()
    print("  Selecciona un día:")
    for i, d in enumerate(dias):
        dt = date.fromisoformat(d)
        print(f"  [{i+1}] {d}  ({dt.strftime('%A')})")
    print("  [0] Volver")

    op = input("\n  Opción: ").strip()
    if not op.isdigit() or int(op) == 0:
        return
    idx = int(op) - 1
    if idx < 0 or idx >= len(dias):
        print("  Opción inválida.")
        pausar()
        return

    fecha = dias[idx]
    reservados = obtener_reservas_fecha(fecha)

    limpiar()
    encabezado(f"HORARIOS — {fecha}")
    print(f"  {'Hora':<18} {'Estado':<14} {'Apartamento'}")
    print("  " + "-" * 44)
    for h in HORARIOS:
        if h in reservados:
            r = reservados[h]
            icono = estado_color(r["estado"])
            print(f"  {formato_hora(h):<18} {icono} {r['estado']:<12} Apto {r['apartamento']}")
        else:
            print(f"  {formato_hora(h):<18} 🟢 Disponible")
    pausar()

def nueva_reserva():
    limpiar()
    encabezado("NUEVA RESERVA")
    apartamento = input("  Número de apartamento: ").strip()
    if not apartamento:
        print("  Apartamento requerido.")
        pausar()
        return

    dias = proximos_dias()
    print("\n  Selecciona el día:")
    for i, d in enumerate(dias):
        dt = date.fromisoformat(d)
        print(f"  [{i+1}] {d}  ({dt.strftime('%A')})")

    op = input("\n  Día: ").strip()
    if not op.isdigit() or not (1 <= int(op) <= len(dias)):
        print("  Opción inválida.")
        pausar()
        return
    fecha = dias[int(op) - 1]

    reservados = obtener_reservas_fecha(fecha)
    disponibles = [h for h in HORARIOS if h not in reservados]
    if not disponibles:
        print("\n  No hay horarios disponibles ese día.")
        pausar()
        return

    print(f"\n  Horarios disponibles el {fecha}:")
    for i, h in enumerate(disponibles):
        print(f"  [{i+1}] {formato_hora(h)}")

    op2 = input("\n  Hora: ").strip()
    if not op2.isdigit() or not (1 <= int(op2) <= len(disponibles)):
        print("  Opción inválida.")
        pausar()
        return
    hora = disponibles[int(op2) - 1]

    ok, msg = crear_reserva(apartamento, fecha, hora)
    print(f"\n  {'✅' if ok else '❌'} {msg}")
    pausar()

def mis_reservas():
    limpiar()
    encabezado("MIS RESERVAS")
    apartamento = input("  Número de apartamento: ").strip()
    if not apartamento:
        pausar()
        return

    with get_conn() as con:
        rows = con.execute(
            "SELECT id, fecha, hora, estado FROM reservas WHERE apartamento=? ORDER BY fecha, hora",
            (apartamento,)
        ).fetchall()

    if not rows:
        print("  No hay reservas para ese apartamento.")
        pausar()
        return

    print(f"\n  {'ID':<6} {'Fecha':<12} {'Hora':<18} {'Estado'}")
    print("  " + "-" * 50)
    for r in rows:
        icono = estado_color(r[3])
        print(f"  {r[0]:<6} {r[1]:<12} {formato_hora(r[2]):<18} {icono} {r[3]}")
    pausar()

def actualizar_mi_reserva():
    limpiar()
    encabezado("ACTUALIZAR RESERVA")
    rid = input("  ID de la reserva a modificar: ").strip()
    if not rid.isdigit():
        print("  ID inválido.")
        pausar()
        return

    reserva = obtener_reserva_por_id(int(rid))
    if not reserva:
        print("  Reserva no encontrada.")
        pausar()
        return

    print(f"\n  Reserva actual:")
    print(f"  Apto: {reserva[1]}  |  Fecha: {reserva[2]}  |  Hora: {formato_hora(reserva[3])}  |  {estado_color(reserva[4])} {reserva[4]}")

    dias = proximos_dias()
    print("\n  Nuevo día:")
    for i, d in enumerate(dias):
        dt = date.fromisoformat(d)
        print(f"  [{i+1}] {d}  ({dt.strftime('%A')})")

    op = input("\n  Día: ").strip()
    if not op.isdigit() or not (1 <= int(op) <= len(dias)):
        print("  Opción inválida.")
        pausar()
        return
    nueva_fecha = dias[int(op) - 1]

    reservados = obtener_reservas_fecha(nueva_fecha)
    # excluir el slot actual si es el mismo día
    disponibles = [h for h in HORARIOS if h not in reservados or (nueva_fecha == reserva[2] and h == reserva[3])]

    print(f"\n  Horarios disponibles el {nueva_fecha}:")
    for i, h in enumerate(disponibles):
        print(f"  [{i+1}] {formato_hora(h)}")

    op2 = input("\n  Hora: ").strip()
    if not op2.isdigit() or not (1 <= int(op2) <= len(disponibles)):
        print("  Opción inválida.")
        pausar()
        return
    nueva_hora = disponibles[int(op2) - 1]

    ok, msg = actualizar_reserva(int(rid), nueva_fecha, nueva_hora)
    print(f"\n  {'✅' if ok else '❌'} {msg}")
    pausar()

def eliminar_mi_reserva():
    limpiar()
    encabezado("ELIMINAR RESERVA")
    rid = input("  ID de la reserva a eliminar: ").strip()
    if not rid.isdigit():
        print("  ID inválido.")
        pausar()
        return

    reserva = obtener_reserva_por_id(int(rid))
    if not reserva:
        print("  Reserva no encontrada.")
        pausar()
        return

    print(f"\n  Reserva a eliminar:")
    print(f"  Apto: {reserva[1]}  |  Fecha: {reserva[2]}  |  Hora: {formato_hora(reserva[3])}  |  {estado_color(reserva[4])} {reserva[4]}")
    conf = input("\n  ¿Confirmar eliminación? (s/n): ").strip().lower()
    if conf == "s":
        eliminar_reserva(int(rid))
        print("  ✅ Reserva eliminada.")
    else:
        print("  Operación cancelada.")
    pausar()

# ──────────────────────────────────────────────
# PANEL ADMINISTRADOR
# ──────────────────────────────────────────────

ADMIN_PIN = "1234"

def panel_admin():
    limpiar()
    encabezado("PANEL ADMINISTRADOR")
    pin = input("  PIN de administrador: ").strip()
    if pin != ADMIN_PIN:
        print("  ❌ PIN incorrecto.")
        pausar()
        return

    while True:
        limpiar()
        encabezado("PANEL ADMINISTRADOR")
        print("  [1] Ver todas las reservas")
        print("  [2] Aprobar reserva")
        print("  [3] Cancelar reserva")
        print("  [4] Eliminar reserva")
        print("  [0] Salir del panel")

        op = input("\n  Opción: ").strip()

        if op == "1":
            admin_ver_todas()
        elif op == "2":
            admin_aprobar()
        elif op == "3":
            admin_cancelar()
        elif op == "4":
            admin_eliminar()
        elif op == "0":
            break
        else:
            print("  Opción inválida.")
            pausar()

def admin_ver_todas():
    limpiar()
    encabezado("TODAS LAS RESERVAS")
    rows = obtener_todas_reservas()
    if not rows:
        print("  No hay reservas registradas.")
        pausar()
        return
    print(f"  {'ID':<6} {'Apto':<8} {'Fecha':<12} {'Hora':<18} {'Estado'}")
    print("  " + "-" * 56)
    for r in rows:
        icono = estado_color(r[4])
        print(f"  {r[0]:<6} {r[1]:<8} {r[2]:<12} {formato_hora(r[3]):<18} {icono} {r[4]}")
    pausar()

def admin_aprobar():
    limpiar()
    encabezado("APROBAR RESERVA")
    rows = obtener_todas_reservas(solo_pendientes=True)
    if not rows:
        print("  No hay reservas pendientes.")
        pausar()
        return
    print(f"  {'ID':<6} {'Apto':<8} {'Fecha':<12} {'Hora'}")
    print("  " + "-" * 46)
    for r in rows:
        print(f"  {r[0]:<6} {r[1]:<8} {r[2]:<12} {formato_hora(r[3])}")

    rid = input("\n  ID a aprobar: ").strip()
    if not rid.isdigit():
        print("  ID inválido.")
        pausar()
        return
    reserva = obtener_reserva_por_id(int(rid))
    if not reserva or reserva[4] != "pendiente":
        print("  Reserva no encontrada o ya procesada.")
        pausar()
        return
    cambiar_estado(int(rid), "aprobada")
    print("  ✅ Reserva aprobada.")
    pausar()

def admin_cancelar():
    limpiar()
    encabezado("CANCELAR RESERVA")
    rid = input("  ID de la reserva: ").strip()
    if not rid.isdigit():
        print("  ID inválido.")
        pausar()
        return
    reserva = obtener_reserva_por_id(int(rid))
    if not reserva:
        print("  Reserva no encontrada.")
        pausar()
        return
    print(f"  Apto: {reserva[1]}  |  Fecha: {reserva[2]}  |  {formato_hora(reserva[3])}")
    conf = input("  ¿Cancelar esta reserva? (s/n): ").strip().lower()
    if conf == "s":
        cambiar_estado(int(rid), "cancelada")
        print("  ✅ Reserva cancelada.")
    pausar()

def admin_eliminar():
    limpiar()
    encabezado("ELIMINAR RESERVA (ADMIN)")
    rid = input("  ID de la reserva a eliminar: ").strip()
    if not rid.isdigit():
        print("  ID inválido.")
        pausar()
        return
    reserva = obtener_reserva_por_id(int(rid))
    if not reserva:
        print("  Reserva no encontrada.")
        pausar()
        return
    print(f"  Apto: {reserva[1]}  |  Fecha: {reserva[2]}  |  {formato_hora(reserva[3])}  |  {reserva[4]}")
    conf = input("  ¿Confirmar eliminación permanente? (s/n): ").strip().lower()
    if conf == "s":
        eliminar_reserva(int(rid))
        print("  ✅ Reserva eliminada.")
    pausar()

# ──────────────────────────────────────────────
# MENÚ PRINCIPAL
# ──────────────────────────────────────────────

def menu_principal():
    while True:
        limpiar()
        encabezado("🏟  CANCHA UNIDAD RESIDENCIAL")
        print("  Horario: 06:00 — 22:00  |  Bloques de 1 hora")
        print()
        print("  [1] Ver horarios disponibles")
        print("  [2] Hacer una reserva")
        print("  [3] Ver mis reservas")
        print("  [4] Actualizar una reserva")
        print("  [5] Eliminar una reserva")
        print("  [6] Panel administrador")
        print("  [0] Salir")

        op = input("\n  Opción: ").strip()

        if op == "1":
            ver_horarios()
        elif op == "2":
            nueva_reserva()
        elif op == "3":
            mis_reservas()
        elif op == "4":
            actualizar_mi_reserva()
        elif op == "5":
            eliminar_mi_reserva()
        elif op == "6":
            panel_admin()
        elif op == "0":
            limpiar()
            print("  Hasta luego!\n")
            break
        else:
            print("  Opción inválida.")
            pausar()


if __name__ == "__main__":
    init_db()
    menu_principal()
