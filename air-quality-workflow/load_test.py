import argparse
import datetime
import os
import random
import statistics
import time

from azure_sql import get_sql_connection


def _generate_row(station_count: int):
    station_id = f"station-{random.randint(1, station_count)}"
    pm25 = round(random.uniform(5, 120), 2)
    pm10 = round(random.uniform(10, 150), 2)
    o3 = round(random.uniform(5, 120), 2)
    aqi = int((pm25 + pm10 + o3) / 3)
    return station_id, datetime.datetime.utcnow(), pm25, pm10, o3, aqi


def _insert_batch(conn, rows):
    query = """
    INSERT INTO air_quality_data (station_id, recorded_at, pm25, pm10, o3, aqi)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    with conn.cursor() as cursor:
        cursor.executemany(query, rows)
    conn.commit()


def run(batch_size, station_count, iterations, pause):
    timings = []
    for i in range(iterations):
        rows = [_generate_row(station_count) for _ in range(batch_size)]
        start = time.perf_counter()
        with get_sql_connection() as conn:
            _insert_batch(conn, rows)
        duration = time.perf_counter() - start
        timings.append(duration)
        print(
            f"[{i + 1}/{iterations}] Inserted {batch_size} rows in {duration:.3f}s "
            f"(avg {(duration / batch_size):.4f}s/row)"
        )
        if pause:
            time.sleep(pause)
    print(
        "Summary:",
        f"min {min(timings):.3f}s, max {max(timings):.3f}s, mean {statistics.mean(timings):.3f}s",
    )


def main():
    parser = argparse.ArgumentParser(description="Load tester for air quality generator")
    parser.add_argument("--batch", type=int, default=20, help="Rows per iteration")
    parser.add_argument("--stations", type=int, default=8, help="Number of stations to simulate")
    parser.add_argument("--iterations", type=int, default=5, help="How many batches to insert")
    parser.add_argument("--pause", type=float, default=0, help="Seconds to pause between rounds")
    args = parser.parse_args()
    run(args.batch, args.stations, args.iterations, args.pause)


if __name__ == "__main__":
    main()
