"""测试 ProcessAirQualitySummary 函数"""
import json
import os
import sys
from unittest.mock import Mock

# 加载配置
cfg = json.load(open("local.settings.json", encoding="utf-8"))
os.environ.update(cfg["Values"])

from ProcessAirQualitySummary import main as process_main
from azure_sql import get_sql_connection


def test_process_summary():
    print("=" * 70)
    print("测试 ProcessAirQualitySummary 函数")
    print("=" * 70)
    print()

    conn = get_sql_connection()
    cur = conn.cursor()

    # 检查初始状态
    cur.execute("SELECT COUNT(*) FROM air_quality_data")
    data_count = cur.fetchone()[0]
    print(f"air_quality_data 表记录数: {data_count}")

    cur.execute("SELECT COUNT(*) FROM air_quality_summary")
    summary_before = cur.fetchone()[0]
    print(f"处理前 air_quality_summary 记录数: {summary_before}")

    cur.execute("SELECT last_version FROM air_quality_sync_state WHERE id = 1")
    last_version = cur.fetchone()[0]
    print(f"上次同步版本: {last_version}")

    cur.execute("SELECT CHANGE_TRACKING_CURRENT_VERSION()")
    current_version = cur.fetchone()[0]
    print(f"当前 Change Tracking 版本: {current_version}")

    conn.close()

    # 模拟 Timer 触发器
    mock_timer = Mock()
    mock_timer.past_due = False

    # 调用函数
    print("\n正在处理变更并生成汇总...", end=" ")
    try:
        process_main(mock_timer)
        print("✓")
    except Exception as e:
        print(f"✗\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 检查处理后的状态
    conn = get_sql_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM air_quality_summary")
    summary_after = cur.fetchone()[0]
    new_summaries = summary_after - summary_before
    print(f"处理后 air_quality_summary 记录数: {summary_after}")
    print(f"新增汇总记录: {new_summaries} 条")

    cur.execute("SELECT last_version FROM air_quality_sync_state WHERE id = 1")
    updated_version = cur.fetchone()[0]
    print(f"更新后的同步版本: {updated_version}")

    # 查看汇总数据
    if summary_after > 0:
        print("\n汇总数据详情:")
        cur.execute("""
            SELECT TOP 5
                window_start, window_end,
                avg_aqi, max_pm25, min_o3, record_count
            FROM air_quality_summary
            ORDER BY window_end DESC
        """)
        print(f"{'窗口开始':<25} {'窗口结束':<25} {'平均AQI':<10} {'最大PM2.5':<10} {'最小O3':<10} {'记录数':<8}")
        print("-" * 100)
        for row in cur.fetchall():
            window_start, window_end, avg_aqi, max_pm25, min_o3, record_count = row
            print(f"{str(window_start):<25} {str(window_end):<25} {avg_aqi:<10.2f} {max_pm25:<10.2f} {min_o3:<10.2f} {record_count:<8}")

        # 显示统计信息
        cur.execute("""
            SELECT
                MIN(avg_aqi) as min_avg_aqi,
                MAX(avg_aqi) as max_avg_aqi,
                AVG(avg_aqi) as overall_avg_aqi,
                SUM(record_count) as total_records
            FROM air_quality_summary
        """)
        row = cur.fetchone()
        print("\n总体统计:")
        print(f"  最小平均 AQI: {row[0]:.2f}")
        print(f"  最大平均 AQI: {row[1]:.2f}")
        print(f"  总体平均 AQI: {row[2]:.2f}")
        print(f"  处理的总记录数: {row[3]}")

    conn.close()

    print("\n" + "=" * 70)
    if new_summaries > 0:
        print(f"✓✓✓ ProcessAirQualitySummary 测试成功！生成了 {new_summaries} 条汇总记录")
    else:
        print("⚠ 注意: 没有生成新的汇总记录（可能没有新的变更）")
    print("=" * 70)


if __name__ == "__main__":
    test_process_summary()
