-- =============================================
-- init.sql - Schema do banco de dados
-- Executado automaticamente pelo PostgreSQL
-- na primeira inicialização do container
-- =============================================

CREATE TABLE IF NOT EXISTS sensors (
    id          SERIAL PRIMARY KEY,
    sensor_id   TEXT    NOT NULL UNIQUE,
    location    TEXT    NOT NULL,
    description TEXT,
    active      BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS noise_readings (
    id               SERIAL PRIMARY KEY,
    sensor_id        TEXT    NOT NULL REFERENCES sensors(sensor_id) ON DELETE CASCADE,
    rms              REAL    NOT NULL,
    noise_level      TEXT    NOT NULL CHECK (noise_level IN ('baixo', 'medio', 'alto', 'muito_alto')),
    sequence         INTEGER NOT NULL,
    device_uptime_ms BIGINT  NOT NULL,
    source_ip        TEXT,
    received_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    capture_hour     SMALLINT    NOT NULL,
    is_silence_period BOOLEAN    NOT NULL DEFAULT FALSE
);

-- Índices para consultas frequentes
CREATE INDEX IF NOT EXISTS idx_readings_sensor_id    ON noise_readings(sensor_id);
CREATE INDEX IF NOT EXISTS idx_readings_received_at  ON noise_readings(received_at DESC);
CREATE INDEX IF NOT EXISTS idx_readings_noise_level  ON noise_readings(noise_level);
CREATE INDEX IF NOT EXISTS idx_readings_silence      ON noise_readings(is_silence_period) WHERE is_silence_period = TRUE;

-- Seed: sensores conhecidos (adicione novos aqui)
INSERT INTO sensors (sensor_id, location, description)
VALUES
    ('sensor_ap1', 'AP1', 'Sensor do Andar/Área 1'),
    ('sensor_ap2', 'AP2', 'Sensor do Andar/Área 2')
ON CONFLICT (sensor_id) DO NOTHING;