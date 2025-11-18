import datetime
import logging
from typing import List, Tuple

import azure.functions as func

from azure_sql import get_sql_connection


def _ensure_sync_state(cursor):
    cursor.execute("SELECT last_version FROM air_quality_sync_state WHERE id = 1")
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute("INSERT INTO air_quality_sync_state (id, last_version) VALUES (1, 0)")
    return 0


def _update_sync_state(cursor, version: int):
    cursor.execute(
        """
        UPDATE air_quality_sync_state
        SET last_version = ?
        WHERE id = 1
        """,
        version,
    )
    if cursor.rowcount == 0:
        cursor.execute(
            "INSERT INTO air_quality_sync_state (id, last_version) VALUES (1, ?)",
            version,
        )


def _collect_changes(cursor, last_version: int) -> Tuple[int, List[Tuple]]:
    cursor.execute("SELECT CHANGE_TRACKING_CURRENT_VERSION()")
    current_version = cursor.fetchone()[0]

    cursor.execute("SELECT CHANGE_TRACKING_MIN_VALID_VERSION(OBJECT_ID('air_quality_data'))")
    min_valid = cursor.fetchone()[0] or 0
    if last_version < min_valid:
        last_version = min_valid

    query = """
    SELECT a.station_id, a.recorded_at, a.pm25, a.pm10, a.o3, a.aqi
    FROM CHANGETABLE(CHANGES air_quality_data, ?) AS ct
    INNER JOIN air_quality_data AS a ON ct.id = a.id
    WHERE ct.SYS_CHANGE_OPERATION IN ('I','U')
    """
    cursor.execute(query, last_version)
    rows = cursor.fetchall()
    return current_version, rows


def _write_summary(cursor, records):
    record_count = len(records)
    if record_count == 0:
        return

    avg_aqi = sum(r[5] for r in records) / record_count
    max_pm25 = max(r[2] for r in records)
    min_o3 = min(r[4] for r in records)
    timestamps = [r[1] for r in records]
    window_start = min(timestamps)
    window_end = max(timestamps)

    cursor.execute(
        """
        INSERT INTO air_quality_summary
            (window_start, window_end, avg_aqi, max_pm25, min_o3, record_count)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        window_start,
        window_end,
        avg_aqi,
        max_pm25,
        min_o3,
        record_count,
    )


def main(mytimer: func.TimerRequest) -> None:  # pylint: disable=unused-argument
    start = datetime.datetime.utcnow()
    try:
        with get_sql_connection() as conn:
            with conn.cursor() as cursor:
                last_version = _ensure_sync_state(cursor)
                current_version, records = _collect_changes(cursor, last_version)
                _write_summary(cursor, records)
                _update_sync_state(cursor, current_version)
            conn.commit()
        duration = (datetime.datetime.utcnow() - start).total_seconds()
        logging.info(
            "Processed %d records; window %.2f s (versions %d → %d)",
            len(records),
            duration,
            last_version,
            current_version,
        )
    except Exception as exc:  # pragma: no cover
        logging.error("Error while processing air-quality changes: %s", exc, exc_info=True)
        raise
