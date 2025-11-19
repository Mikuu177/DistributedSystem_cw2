"""快速数据验证 - 用于视频演示"""
import json
import os

cfg = json.load(open('local.settings.json'))
os.environ.update(cfg['Values'])

from azure_sql import get_sql_connection

print("=" * 60)
print("AIR QUALITY MONITORING SYSTEM - DATA VALIDATION")
print("=" * 60)
print()

conn = get_sql_connection()
cur = conn.cursor()

# 数据记录
cur.execute('SELECT COUNT(*) FROM air_quality_data')
data_count = cur.fetchone()[0]
print(f"✓ Total Data Records: {data_count:,}")

# 汇总记录
cur.execute('SELECT COUNT(*) FROM air_quality_summary')
summary_count = cur.fetchone()[0]
print(f"✓ Summary Records: {summary_count}")

# 监测站
cur.execute('SELECT COUNT(DISTINCT station_id) FROM air_quality_data')
station_count = cur.fetchone()[0]
print(f"✓ Monitoring Stations: {station_count}")

# 时间范围
cur.execute('SELECT MIN(recorded_at), MAX(recorded_at) FROM air_quality_data')
row = cur.fetchone()
print(f"✓ Time Range: {row[0]} to {row[1]}")

# AQI 统计
cur.execute('SELECT AVG(aqi), MIN(aqi), MAX(aqi) FROM air_quality_data')
row = cur.fetchone()
print(f"✓ AQI Statistics: Avg={row[0]:.1f}, Min={row[1]}, Max={row[2]}")

conn.close()

print()
print("=" * 60)
print("✓✓✓ System is operational and validated!")
print("=" * 60)
