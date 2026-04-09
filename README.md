# Cancha Unidad Residencial

App de consola en Python para gestionar reservas de la cancha de una unidad residencial.

## Caracteristicasdd

- Ver horarios disponibles por dia (proximos 7 dias)
- Reservar un bloque de 1 hora por apartamento
- Ver, actualizar y eliminar reservas propias
- Panel de administrador para aprobar, cancelar y eliminar reservas
- Base de datos local SQLite (sin instalacion adicional)

## Requisitos

- Python 3.6 o superior
- Sin dependencias externas

## Uso

```bash
python3 main.py
```

## Estructura MVC

```
App-reserva/
├── main.py                          # Punto de entrada y router principal
├── models/
│   └── reserva.py                   # Base de datos, consultas y reglas de dominio
├── views/
│   └── consola.py                   # Toda la interfaz (menus, inputs, outputs)
├── controllers/
│   ├── reserva_controller.py        # Logica de reservas del residente
│   └── admin_controller.py          # Logica del panel administrador
└── cancha.db                        # SQLite (se crea automaticamente)
```

## Menu principal

| Opcion | Funcion |
|--------|---------|
| `1` | Ver horarios disponibles |
| `2` | Hacer una reserva |
| `3` | Ver mis reservas |
| `4` | Actualizar una reserva |
| `5` | Eliminar una reserva |
| `6` | Panel administrador |

## Panel administrador

Acceso con PIN (por defecto: `1234`, configurable en `models/reserva.py` variable `ADMIN_PIN`).

| Opcion | Funcion |
|--------|---------|
| `1` | Ver todas las reservas |
| `2` | Aprobar reservas pendientes |
| `3` | Cancelar una reserva |
| `4` | Eliminar una reserva permanentemente |

## Estados de una reserva

| Estado | Descripcion |
|--------|-------------|
| Pendiente | Recien creada, espera aprobacion del admin |
| Aprobada | Confirmada por el administrador |
| Cancelada | Rechazada o cancelada por el admin |

## Reglas de negocio

- Bloques de **1 hora**, de **06:00 a 22:00**
- No se pueden hacer dos reservas en el mismo horario
- Al actualizar una reserva, vuelve a estado *pendiente*
- Se puede reservar con hasta **7 dias de anticipacion**
