import sqlite3
from datetime import date, timedelta

DB_FILE = "cancha.db"
HORARIOS = list(range(6, 22))   # 06:00 – 22:00
DIAS_ANTICIPACION = 7
ADMIN_PIN = "1234"


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


# ── Consultas ──────────────────────────────────

def reservas_por_fecha(fecha: str) -> dict:
    with get_conn() as con:
        cur = con.execute(
            "SELECT hora, apartamento, estado FROM reservas WHERE fecha=? ORDER BY hora",
            (fecha,)
        )
        return {row[0]: {"apartamento": row[1], "estado": row[2]} for row in cur}


def reservas_por_apartamento(apartamento: str) -> list:
    with get_conn() as con:
        return con.execute(
            "SELECT id, fecha, hora, estado FROM reservas WHERE apartamento=? ORDER BY fecha, hora",
            (apartamento,)
        ).fetchall()


def todas_las_reservas(solo_pendientes=False) -> list:
    with get_conn() as con:
        query = "SELECT id, apartamento, fecha, hora, estado FROM reservas"
        if solo_pendientes:
            query += " WHERE estado='pendiente'"
        query += " ORDER BY fecha, hora"
        return con.execute(query).fetchall()


def buscar_por_id(rid: int):
    with get_conn() as con:
        return con.execute(
            "SELECT id, apartamento, fecha, hora, estado FROM reservas WHERE id=?", (rid,)
        ).fetchone()


# ── Escritura ──────────────────────────────────

def insertar_reserva(apartamento: str, fecha: str, hora: int, creada_en: str):
    with get_conn() as con:
        con.execute(
            "INSERT INTO reservas (apartamento, fecha, hora, estado, creada_en) VALUES (?,?,?,?,?)",
            (apartamento, fecha, hora, "pendiente", creada_en)
        )


def mover_reserva(rid: int, nueva_fecha: str, nueva_hora: int):
    with get_conn() as con:
        con.execute(
            "UPDATE reservas SET fecha=?, hora=?, estado='pendiente' WHERE id=?",
            (nueva_fecha, nueva_hora, rid)
        )


def borrar_reserva(rid: int):
    with get_conn() as con:
        con.execute("DELETE FROM reservas WHERE id=?", (rid,))


def set_estado(rid: int, estado: str):
    with get_conn() as con:
        con.execute("UPDATE reservas SET estado=? WHERE id=?", (estado, rid))


# ── Utilidades de dominio ──────────────────────

def proximos_dias() -> list:
    hoy = date.today()
    return [(hoy + timedelta(days=i)).isoformat() for i in range(DIAS_ANTICIPACION)]


def horarios_disponibles(fecha: str, excluir_hora: int = None) -> list:
    ocupados = reservas_por_fecha(fecha)
    return [
        h for h in HORARIOS
        if h not in ocupados or h == excluir_hora
    ]
