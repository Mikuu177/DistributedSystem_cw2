"""测试 GenerateAirQualityData 函数"""
import json
import os
import sys
from unittest.mock import Mock

# 加载配置
cfg = json.load(open("local.settings.json", encoding="utf-8"))
os.environ.update(cfg["Values"])

# 设置测试环境变量
os.environ["BATCH_SIZE"] = "10"
os.environ["STATION_COUNT"] = "5"

from GenerateAirQualityData import main as generate_main
from azure_sql import get_sql_connection


def test_generate():
    print("=" * 70)
    print("测试 GenerateAirQualityData 函数")
    print("=" * 70)
    print(f"\n配置:")
    print(f"  BATCH_SIZE: {os.environ['BATCH_SIZE']} 条记录")
    print(f"  STATION_COUNT: {os.environ['STATION_COUNT']} 个监测站")
    print()

    # 检查初始状态
    conn = get_sql_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM air_quality_data")
    before_count = cur.fetchone()[0]
    print(f"插入前记录数: {before_count}")
    conn.close()

    # 模拟 Timer 触发器
    mock_timer = Mock()
    mock_timer.past_due = False

    # 调用函数
    print("\n正在生成数据...", end=" ")
    try:
        generate_main(mock_timer)
        print("✓")
    except Exception as e:
        print(f"✗\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 检查插入后的状态
    conn = get_sql_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM air_quality_data")
    after_count = cur.fetchone()[0]
    inserted = after_count - before_count
    print(f"插入后记录数: {after_count}")
    print(f"新增记录: {inserted} 条")

    # 查看样本数据
    print("\n样本数据 (最新 5 条):")
    cur.execute("""
        SELECT TOP 5 station_id, recorded_at, pm25, pm10, o3, aqi
        FROM air_quality_data
        ORDER BY recorded_at DESC
    """)
    print(f"{'站点ID':<15} {'记录时间':<25} {'PM2.5':<8} {'PM10':<8} {'O3':<8} {'AQI':<5}")
    print("-" * 70)
    for row in cur.fetchall():
        station_id, recorded_at, pm25, pm10, o3, aqi = row
        print(f"{station_id:<15} {str(recorded_at):<25} {pm25:<8.2f} {pm10:<8.2f} {o3:<8.2f} {aqi:<5}")

    # 统计各站点的数据量
    print("\n各监测站数据统计:")
    cur.execute("""
        SELECT station_id, COUNT(*) as count
        FROM air_quality_data
        GROUP BY station_id
        ORDER BY station_id
    """)
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} 条记录")

    conn.close()

    print("\n" + "=" * 70)
    if inserted == int(os.environ["BATCH_SIZE"]):
        print(f"✓✓✓ GenerateAirQualityData 测试成功！插入了 {inserted} 条记录")
    else:
        print(f"⚠ 警告: 预期插入 {os.environ['BATCH_SIZE']} 条，实际插入 {inserted} 条")
    print("=" * 70)


if __name__ == "__main__":
    test_generate()
