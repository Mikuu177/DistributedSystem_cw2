"""
性能测试脚本 - 测试不同负载下的 Serverless Workflow 性能
所有数据都是真实运行获得，不编造任何数据
"""
import json
import os
import sys
import time
import tracemalloc
import psutil
from datetime import datetime
from unittest.mock import Mock
import csv

# 加载配置
cfg = json.load(open("local.settings.json", encoding="utf-8"))
os.environ.update(cfg["Values"])

from GenerateAirQualityData import main as generate_main
from ProcessAirQualitySummary import main as process_main
from azure_sql import get_sql_connection


class PerformanceMonitor:
    """性能监控类"""

    def __init__(self):
        self.process = psutil.Process()
        self.start_time = None
        self.end_time = None
        self.start_memory = None
        self.end_memory = None
        self.peak_memory = 0

    def start(self):
        """开始监控"""
        tracemalloc.start()
        self.start_time = time.time()
        self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB

    def stop(self):
        """停止监控"""
        self.end_time = time.time()
        self.end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        current, peak = tracemalloc.get_traced_memory()
        self.peak_memory = peak / 1024 / 1024  # MB
        tracemalloc.stop()

    def get_stats(self):
        """获取性能统计"""
        return {
            'duration': self.end_time - self.start_time,
            'start_memory_mb': self.start_memory,
            'end_memory_mb': self.end_memory,
            'memory_increase_mb': self.end_memory - self.start_memory,
            'peak_memory_mb': self.peak_memory,
            'cpu_percent': self.process.cpu_percent(interval=0.1)
        }


def clear_database():
    """清空数据库以便进行干净的测试"""
    conn = get_sql_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM air_quality_summary")
    cur.execute("DELETE FROM air_quality_data")
    cur.execute("UPDATE air_quality_sync_state SET last_version = 0 WHERE id = 1")
    conn.commit()
    conn.close()
    print("  数据库已清空")


def get_database_stats():
    """获取数据库统计信息"""
    conn = get_sql_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM air_quality_data")
    data_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM air_quality_summary")
    summary_count = cur.fetchone()[0]

    conn.close()
    return data_count, summary_count


def run_single_test(batch_size, station_count, iteration):
    """运行单次测试"""
    print(f"\n  测试 {iteration}: BATCH_SIZE={batch_size}, STATION_COUNT={station_count}")

    # 设置环境变量
    os.environ["BATCH_SIZE"] = str(batch_size)
    os.environ["STATION_COUNT"] = str(station_count)

    mock_timer = Mock()
    mock_timer.past_due = False

    # 测试数据生成函数
    print("    - 测试 GenerateAirQualityData...", end=" ")
    monitor_gen = PerformanceMonitor()
    monitor_gen.start()

    try:
        generate_main(mock_timer)
        monitor_gen.stop()
        gen_stats = monitor_gen.get_stats()
        print(f"✓ ({gen_stats['duration']:.3f}s)")
    except Exception as e:
        print(f"✗ 错误: {e}")
        return None

    # 短暂延迟确保数据已提交
    time.sleep(0.5)

    # 测试汇总处理函数
    print("    - 测试 ProcessAirQualitySummary...", end=" ")
    monitor_proc = PerformanceMonitor()
    monitor_proc.start()

    try:
        process_main(mock_timer)
        monitor_proc.stop()
        proc_stats = monitor_proc.get_stats()
        print(f"✓ ({proc_stats['duration']:.3f}s)")
    except Exception as e:
        print(f"✗ 错误: {e}")
        return None

    # 获取数据库统计
    data_count, summary_count = get_database_stats()

    # 返回完整的测试结果
    result = {
        'iteration': iteration,
        'batch_size': batch_size,
        'station_count': station_count,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),

        # GenerateAirQualityData 性能
        'gen_duration_sec': gen_stats['duration'],
        'gen_memory_increase_mb': gen_stats['memory_increase_mb'],
        'gen_peak_memory_mb': gen_stats['peak_memory_mb'],
        'gen_cpu_percent': gen_stats['cpu_percent'],

        # ProcessAirQualitySummary 性能
        'proc_duration_sec': proc_stats['duration'],
        'proc_memory_increase_mb': proc_stats['memory_increase_mb'],
        'proc_peak_memory_mb': proc_stats['peak_memory_mb'],
        'proc_cpu_percent': proc_stats['cpu_percent'],

        # 总体性能
        'total_duration_sec': gen_stats['duration'] + proc_stats['duration'],

        # 数据库统计
        'total_data_records': data_count,
        'total_summary_records': summary_count,

        # 吞吐量（每秒处理的记录数）
        'throughput_records_per_sec': batch_size / gen_stats['duration'] if gen_stats['duration'] > 0 else 0
    }

    print(f"    - 总耗时: {result['total_duration_sec']:.3f}s")
    print(f"    - 吞吐量: {result['throughput_records_per_sec']:.2f} 记录/秒")

    return result


def run_performance_tests():
    """运行完整的性能测试套件"""
    print("=" * 80)
    print("Azure Functions Serverless Workflow - 性能测试")
    print("=" * 80)
    print(f"\n开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n测试配置：")
    print("  - 平台: Azure Functions (Python)")
    print("  - 数据库: Azure SQL Database")
    print("  - 触发机制: Timer Trigger + Change Tracking")

    # 测试配置组合
    test_configs = [
        # (batch_size, station_count, iterations)
        (20, 5, 3),    # 小负载
        (50, 8, 3),    # 中等负载
        (100, 10, 3),  # 大负载
        (200, 15, 2),  # 超大负载
    ]

    all_results = []

    for batch_size, station_count, iterations in test_configs:
        print(f"\n{'=' * 80}")
        print(f"测试场景: BATCH_SIZE={batch_size}, STATION_COUNT={station_count}")
        print(f"{'=' * 80}")

        for i in range(1, iterations + 1):
            # 每次测试前清空数据库
            clear_database()

            result = run_single_test(batch_size, station_count, i)
            if result:
                all_results.append(result)

            # 测试之间短暂延迟
            if i < iterations:
                time.sleep(1)

    return all_results


def save_results_to_csv(results, filename='performance_results.csv'):
    """将结果保存到 CSV 文件"""
    if not results:
        print("没有结果可保存")
        return

    fieldnames = results[0].keys()

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✓ 结果已保存到: {filename}")


def generate_summary_report(results):
    """生成性能总结报告"""
    if not results:
        print("没有结果可生成报告")
        return

    print("\n" + "=" * 80)
    print("性能测试总结报告")
    print("=" * 80)

    # 按配置分组统计
    configs = {}
    for r in results:
        key = (r['batch_size'], r['station_count'])
        if key not in configs:
            configs[key] = []
        configs[key].append(r)

    print(f"\n{'配置':<25} {'平均总耗时(s)':<15} {'平均吞吐量':<20} {'平均CPU%':<12} {'内存增长(MB)':<15}")
    print("-" * 100)

    for (batch_size, station_count), records in sorted(configs.items()):
        avg_duration = sum(r['total_duration_sec'] for r in records) / len(records)
        avg_throughput = sum(r['throughput_records_per_sec'] for r in records) / len(records)
        avg_cpu_gen = sum(r['gen_cpu_percent'] for r in records) / len(records)
        avg_cpu_proc = sum(r['proc_cpu_percent'] for r in records) / len(records)
        avg_memory = sum(r['gen_memory_increase_mb'] + r['proc_memory_increase_mb'] for r in records) / len(records)

        config_str = f"BS={batch_size}, SC={station_count}"
        print(f"{config_str:<25} {avg_duration:<15.3f} {avg_throughput:<20.2f} {(avg_cpu_gen+avg_cpu_proc)/2:<12.1f} {avg_memory:<15.2f}")

    # 详细统计
    print("\n" + "=" * 80)
    print("详细性能指标")
    print("=" * 80)

    for (batch_size, station_count), records in sorted(configs.items()):
        print(f"\n配置: BATCH_SIZE={batch_size}, STATION_COUNT={station_count} ({len(records)} 次测试)")
        print("-" * 80)

        avg_gen_time = sum(r['gen_duration_sec'] for r in records) / len(records)
        avg_proc_time = sum(r['proc_duration_sec'] for r in records) / len(records)
        avg_gen_mem = sum(r['gen_peak_memory_mb'] for r in records) / len(records)
        avg_proc_mem = sum(r['proc_peak_memory_mb'] for r in records) / len(records)

        print(f"  GenerateAirQualityData:")
        print(f"    - 平均执行时间: {avg_gen_time:.3f}s")
        print(f"    - 峰值内存使用: {avg_gen_mem:.2f} MB")
        print(f"  ProcessAirQualitySummary:")
        print(f"    - 平均执行时间: {avg_proc_time:.3f}s")
        print(f"    - 峰值内存使用: {avg_proc_mem:.2f} MB")
        print(f"  吞吐量: {sum(r['throughput_records_per_sec'] for r in records) / len(records):.2f} 记录/秒")

    # 可扩展性分析
    print("\n" + "=" * 80)
    print("可扩展性分析")
    print("=" * 80)

    sorted_configs = sorted(configs.items(), key=lambda x: x[0][0])
    if len(sorted_configs) >= 2:
        print("\n负载增加对性能的影响:")
        for i in range(len(sorted_configs) - 1):
            (bs1, sc1), records1 = sorted_configs[i]
            (bs2, sc2), records2 = sorted_configs[i + 1]

            avg_time1 = sum(r['total_duration_sec'] for r in records1) / len(records1)
            avg_time2 = sum(r['total_duration_sec'] for r in records2) / len(records2)

            load_increase = ((bs2 / bs1) - 1) * 100
            time_increase = ((avg_time2 / avg_time1) - 1) * 100

            print(f"  {bs1}→{bs2} 条记录:")
            print(f"    - 负载增加: {load_increase:.1f}%")
            print(f"    - 执行时间增加: {time_increase:.1f}%")
            print(f"    - 扩展效率: {'良好' if time_increase < load_increase else '需优化'}")

    print("\n" + "=" * 80)
    print(f"测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总测试次数: {len(results)}")
    print("=" * 80)


def main():
    """主函数"""
    try:
        # 运行性能测试
        results = run_performance_tests()

        # 保存结果到 CSV
        save_results_to_csv(results, 'performance_results.csv')

        # 生成总结报告
        generate_summary_report(results)

        print("\n✓✓✓ 性能测试完成！✓✓✓")
        print("\n生成的文件:")
        print("  - performance_results.csv (详细数据)")
        print("\n下一步:")
        print("  1. 查看 performance_results.csv 了解详细数据")
        print("  2. 可以用 Excel 或 Python 生成图表")
        print("  3. 将结果写入报告文档")

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
