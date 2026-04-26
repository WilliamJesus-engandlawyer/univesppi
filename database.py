# =============================================
# database.py - Camada de acesso ao banco
# =============================================
# Toda interação com o PostgreSQL fica aqui.
# main.py não sabe nada sobre SQL.
# =============================================

from datetime import datetime, timezone
import os
import psycopg2
import psycopg2.extras
from psycopg2.pool import ThreadedConnectionPool


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://noiseuser:noisepass@localhost:5432/noisedb",
)

_pool: ThreadedConnectionPool | None = None


def _is_silence_period(hour: int) -> bool:
    """Lei do Silêncio: 22h–6h"""
    return hour >= 22 or hour < 6


class Database:
    """Repositório de leituras de ruído."""

    async def connect(self):
        global _pool
        _pool = ThreadedConnectionPool(minconn=1, maxconn=10, dsn=DATABASE_URL)
        print(f"🔌 Pool de conexões criado: {DATABASE_URL.split('@')[-1]}")

    async def disconnect(self):
        if _pool:
            _pool.closeall()

    def _get_conn(self):
        return _pool.getconn()

    def _put_conn(self, conn):
        _pool.putconn(conn)

    # --------------------------------------------------

    async def save_reading(self, data, source_ip: str) -> int:
        """Persiste uma leitura e garante que o sensor exista."""
        now        = datetime.now(tz=timezone.utc)
        local_hour = datetime.now().hour          # hora local do servidor
        silence    = _is_silence_period(local_hour)

        conn = self._get_conn()
        try:
            with conn:
                with conn.cursor() as cur:
                    # Upsert do sensor (cria se não existir)
                    cur.execute(
                        """
                        INSERT INTO sensors (sensor_id, location)
                        VALUES (%s, %s)
                        ON CONFLICT (sensor_id) DO UPDATE
                            SET location = EXCLUDED.location
                        """,
                        (data.sensor_id, data.location),
                    )

                    # Insere leitura
                    cur.execute(
                        """
                        INSERT INTO noise_readings
                            (sensor_id, rms, noise_level, sequence,
                             device_uptime_ms, source_ip, received_at,
                             capture_hour, is_silence_period)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (
                            data.sensor_id,
                            data.rms,
                            data.noise_level,
                            data.sequence,
                            data.device_uptime_ms,
                            source_ip,
                            now,
                            local_hour,
                            silence,
                        ),
                    )
                    row = cur.fetchone()
                    return row[0]
        finally:
            self._put_conn(conn)

    async def get_readings(self, limit: int = 100) -> list[dict]:
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT
                        r.id,
                        r.sensor_id,
                        s.location,
                        r.rms,
                        r.noise_level,
                        r.sequence,
                        r.device_uptime_ms,
                        r.source_ip,
                        to_char(r.received_at AT TIME ZONE 'America/Sao_Paulo',
                                'YYYY-MM-DD HH24:MI:SS') AS received_at,
                        r.capture_hour,
                        r.is_silence_period
                    FROM noise_readings r
                    JOIN sensors s USING (sensor_id)
                    ORDER BY r.id DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                return [dict(row) for row in cur.fetchall()]
        finally:
            self._put_conn(conn)

    async def get_sensors(self) -> list[dict]:
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT
                        s.sensor_id,
                        s.location,
                        s.description,
                        s.active,
                        COUNT(r.id)           AS total_readings,
                        MAX(r.received_at)    AS last_reading_at
                    FROM sensors s
                    LEFT JOIN noise_readings r USING (sensor_id)
                    GROUP BY s.sensor_id, s.location, s.description, s.active
                    ORDER BY s.sensor_id
                    """
                )
                return [dict(row) for row in cur.fetchall()]
        finally:
            self._put_conn(conn)

    async def count_readings(self) -> int:
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM noise_readings")
                return cur.fetchone()[0]
        finally:
            self._put_conn(conn)