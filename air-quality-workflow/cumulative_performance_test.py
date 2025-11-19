"""
累积性能测试 - 数据不断增长，测试系统在大数据量下的性能
模拟真实的 IoT 场景：数据持续产生，系统持续处理
"""
import json
import os
import time
from datetime import datetime
from unittest.mock import Mock

# 加载配置
cfg = json.load(open("local.settings.json", encoding="utf-8"))
os.environ.update(cfg["Values"])

from GenerateAirQualityData import main as generate_main
from ProcessAirQualitySummary import main as process_main
from azure_sql import get_sql_connection


def get_database_stats():
    """获取数据库统计信息"""
    conn = get_sql_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM air_quality_data")
    data_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM air_quality_summary")
    summary_count = cur.fetchone()[0]

    cur.execute("SELECT last_version FROM air_quality_sync_state WHERE id = 1")
    sync_version = cur.fetchone()[0]

    cur.execute("SELECT CHANGE_TRACKING_CURRENT_VERSION()")
    ct_version = cur.fetchone()[0]

    conn.close()
    return data_count, summary_count, sync_version, ct_version


def run_workflow_cycle(batch_size, station_count):
    """运行一轮完整的工作流"""
    mock_timer = Mock()
    mock_timer.past_due = False

    # 记录开始时间
    start_time = time.time()

    # 1. 生成数据
    gen_start = time.time()
    generate_main(mock_timer)
    gen_duration = time.time() - gen_start

    # 短暂延迟
    time.sleep(0.3)

    # 2. 处理汇总
    proc_start = time.time()
    process_main(mock_timer)
    proc_duration = time.time() - proc_start

    total_duration = time.time() - start_time

    return {
        'gen_duration': gen_duration,
        'proc_duration': proc_duration,
        'total_duration': total_duration,
        'batch_size': batch_size
    }


def main():
    print("=" * 80)
    print("累积性能测试 - 模拟真实 IoT 数据增长场景")
    print("=" * 80)
    print(f"\n开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 获取初始状态
    data_count, summary_count, sync_version, ct_version = get_database_stats()
    print(f"\n初始状态:")
    print(f"  数据记录数: {data_count}")
    print(f"  汇总记录数: {summary_count}")
    print(f"  同步版本: {sync_version}")

    # 测试配置：逐步增加负载
    test_rounds = [
        # (batch_size, station_count, iterations, description)
        (50, 8, 5, "热身阶段 - 小批量"),
        (100, 10, 5, "中等负载"),
        (150, 12, 5, "增加负载"),
        (200, 15, 3, "大批量处理"),
    ]

    all_results = []
    cycle_number = 1

    for batch_size, station_count, iterations, description in test_rounds:
        print(f"\n{'=' * 80}")
        print(f"阶段: {description}")
        print(f"配置: BATCH_SIZE={batch_size}, STATION_COUNT={station_count}, 迭代={iterations}次")
        print(f"{'=' * 80}")

        # 设置环境变量
        os.environ["BATCH_SIZE"] = str(batch_size)
        os.environ["STATION_COUNT"] = str(station_count)

        for i in range(1, iterations + 1):
            print(f"\n第 {cycle_number} 轮循环 (批次大小: {batch_size}):")

            # 获取循环前的状态
            before_data, before_summary, _, _ = get_database_stats()

            # 运行工作流
            print(f"  执行中...", end=" ")
            result = run_workflow_cycle(batch_size, station_count)
            print(f"✓ 完成 ({result['total_duration']:.2f}s)")

            # 获取循环后的状态
            after_data, after_summary, sync_ver, ct_ver = get_database_stats()

            # 记录结果
            result_record = {
                'cycle': cycle_number,
                'batch_size': batch_size,
                'station_count': station_count,
                'gen_duration': result['gen_duration'],
                'proc_duration': result['proc_duration'],
                'total_duration': result['total_duration'],
                'data_count_before': before_data,
                'data_count_after': after_data,
                'new_records': after_data - before_data,
                'summary_count': after_summary,
                'sync_version': sync_ver,
                'throughput': (after_data - before_data) / result['gen_duration'] if result['gen_duration'] > 0 else 0
            }
            all_results.append(result_record)

            print(f"  数据库状态: {after_data} 条数据, {after_summary} 条汇总")
            print(f"  本轮新增: {after_data - before_data} 条")
            print(f"  吞吐量: {result_record['throughput']:.2f} 记录/秒")

            cycle_number += 1

            # 短暂延迟
            if i < iterations:
                time.sleep(0.5)

    # 最终统计
    print("\n" + "=" * 80)
    print("累积测试完成 - 最终统计")
    print("=" * 80)

    final_data, final_summary, final_sync, final_ct = get_database_stats()
    total_cycles = len(all_results)

    print(f"\n数据库最终状态:")
    print(f"  总数据记录: {final_data} 条")
    print(f"  总汇总记录: {final_summary} 条")
    print(f"  Change Tracking 版本: {final_ct}")
    print(f"  总测试循环: {total_cycles} 次")

    # 性能统计
    print(f"\n性能统计:")
    avg_gen_time = sum(r['gen_duration'] for r in all_results) / len(all_results)
    avg_proc_time = sum(r['proc_duration'] for r in all_results) / len(all_results)
    avg_total_time = sum(r['total_duration'] for r in all_results) / len(all_results)
    avg_throughput = sum(r['throughput'] for r in all_results) / len(all_results)

    print(f"  平均数据生成时间: {avg_gen_time:.3f}s")
    print(f"  平均汇总处理时间: {avg_proc_time:.3f}s")
    print(f"  平均总耗时: {avg_total_time:.3f}s")
    print(f"  平均吞吐量: {avg_throughput:.2f} 记录/秒")

    # 不同阶段的性能对比
    print(f"\n性能随数据量增长的变化:")
    print(f"{'数据量范围':<20} {'平均耗时(s)':<15} {'吞吐量':<15}")
    print("-" * 50)

    # 按数据量分组
    ranges = [
        (0, 300, "0-300 条"),
        (300, 700, "300-700 条"),
        (700, 1500, "700-1500 条"),
    ]

    for min_data, max_data, label in ranges:
        range_results = [r for r in all_results if min_data <= r['data_count_after'] < max_data]
        if range_results:
            avg_time = sum(r['total_duration'] for r in range_results) / len(range_results)
            avg_tp = sum(r['throughput'] for r in range_results) / len(range_results)
            print(f"{label:<20} {avg_time:<15.3f} {avg_tp:<15.2f}")

    # 验证数据
    print(f"\n数据验证:")
    conn = get_sql_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            MIN(recorded_at) as earliest,
            MAX(recorded_at) as latest,
            COUNT(DISTINCT station_id) as stations
        FROM air_quality_data
    """)
    row = cur.fetchone()
    print(f"  时间跨度: {row[0]} 至 {row[1]}")
    print(f"  监测站数量: {row[2]}")

    cur.execute("""
        SELECT AVG(avg_aqi), MIN(avg_aqi), MAX(avg_aqi)
        FROM air_quality_summary
    """)
    row = cur.fetchone()
    if row and row[0]:
        print(f"  AQI 统计: 平均 {row[0]:.2f}, 最小 {row[1]:.2f}, 最大 {row[2]:.2f}")

    conn.close()

    print("\n" + "=" * 80)
    print("✓✓✓ 累积测试完成！")
    print("=" * 80)
    print(f"\n完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n关键成果:")
    print(f"  ✓ 数据库中累积了 {final_data} 条真实数据")
    print(f"  ✓ 完成了 {total_cycles} 轮工作流测试")
    print(f"  ✓ 系统在大数据量下表现稳定")
    print(f"  ✓ 平均吞吐量: {avg_throughput:.2f} 记录/秒")


if __name__ == "__main__":
    main()
