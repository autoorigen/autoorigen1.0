"""Copia los datos de data/autoorigen.db (SQLite) a Supabase (PostgreSQL).

Uso, desde la carpeta del proyecto y con el venv activo:
    python migrar_a_supabase.py

- Crea las tablas en Supabase si no existen.
- Si alguna tabla de Supabase ya tiene datos, se detiene sin copiar nada
  (para no duplicar).
- Todo va en una sola transacción: o se copia completo, o no se copia nada.
- No modifica ni borra el archivo SQLite original.
"""
import sqlite3
import sys

import psycopg

from autoorigen.config import Config
from autoorigen.db import SCHEMA, TABLAS


def main():
    ruta_sqlite = Config.DB_PATH
    url = getattr(Config, "DATABASE_URL", None)

    if not ruta_sqlite.exists():
        sys.exit(f"No encontré la base SQLite en {ruta_sqlite}")
    if not url:
        sys.exit("Falta DATABASE_URL en el archivo .env del proyecto.")

    origen = sqlite3.connect(ruta_sqlite)
    origen.row_factory = sqlite3.Row

    with psycopg.connect(url) as destino:
        destino.execute(SCHEMA)

        for tabla in TABLAS:
            cantidad = destino.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
            if cantidad:
                sys.exit(
                    f"La tabla '{tabla}' en Supabase ya tiene {cantidad} filas. "
                    "No copié nada para no duplicar datos."
                )

        for tabla in TABLAS:
            existe = origen.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (tabla,)
            ).fetchone()
            if not existe:
                print(f"{tabla}: no existe en SQLite, se omite")
                continue

            filas = origen.execute(f"SELECT * FROM {tabla} ORDER BY id").fetchall()
            if filas:
                columnas = filas[0].keys()
                sql = (
                    f"INSERT INTO {tabla} ({', '.join(columnas)}) "
                    f"VALUES ({', '.join(['%s'] * len(columnas))})"
                )
                with destino.cursor() as cur:
                    cur.executemany(sql, [tuple(f) for f in filas])

            # Ajusta el contador de IDs para que los registros nuevos
            # continúen después del ID más alto copiado.
            destino.execute(
                f"SELECT setval(pg_get_serial_sequence('{tabla}', 'id'), "
                f"COALESCE((SELECT MAX(id) FROM {tabla}), 0) + 1, false)"
            )
            print(f"{tabla}: {len(filas)} filas copiadas")

    origen.close()
    print("\nListo. Revisa los datos en el panel de Supabase (Table Editor).")


if __name__ == "__main__":
    main()
