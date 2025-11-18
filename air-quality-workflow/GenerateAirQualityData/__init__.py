import datetime
import logging
import os
import random

import azure.functions as func

from azure_sql import get_sql_connection


def _generate_readings(batch_size: int, station_count: int):
    readings = []
    now = datetime.datetime.utcnow()
    for _ in range(batch_size):
        station_id = f"station-{random.randint(1, station_count)}"
        pm25 = round(random.uniform(5, 120), 2)
        pm10 = round(random.uniform(10, 150), 2)
        o3 = round(random.uniform(5, 120), 2)
        aqi = int((pm25 + pm10 + o3) / 3)
        readings.append(
            (station_id, now, pm25, pm10, o3, aqi),
        )
    return readings


def _write_batch(readings):
    query = """
    INSERT INTO air_quality_data (station_id, recorded_at, pm25, pm10, o3, aqi)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    with get_sql_connection() as conn:
        with conn.cursor() as cursor:
            cursor.executemany(query, readings)
        conn.commit()


def main(mytimer: func.TimerRequest) -> None:
    batch_size = int(os.getenv("BATCH_SIZE", "20"))
    station_count = int(os.getenv("STATION_COUNT", "8"))
    start = datetime.datetime.utcnow()
    readings = _generate_readings(batch_size, station_count)
    try:
        _write_batch(readings)
        duration = (datetime.datetime.utcnow() - start).total_seconds()
        logging.info(
            "Inserted %d air-quality records from %d stations in %.2fs",
            batch_size,
            station_count,
            duration,
        )
    except Exception as exc:  # pragma: no cover
        logging.error("Failed to insert air-quality data: %s", exc, exc_info=True)
        raise
