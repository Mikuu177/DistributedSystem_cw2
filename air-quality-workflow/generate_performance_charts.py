"""
生成性能分析图表
基于真实的性能测试数据生成可视化图表
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

# 设置中文字体支持
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# 读取性能测试数据
df = pd.read_csv('performance_results.csv')

# 按配置分组计算平均值
config_groups = df.groupby(['batch_size', 'station_count']).agg({
    'total_duration_sec': 'mean',
    'throughput_records_per_sec': 'mean',
    'gen_duration_sec': 'mean',
    'proc_duration_sec': 'mean',
    'gen_peak_memory_mb': 'mean',
    'proc_peak_memory_mb': 'mean',
    'gen_cpu_percent': 'mean',
    'proc_cpu_percent': 'mean'
}).reset_index()

print("生成性能分析图表...")
print(f"数据点: {len(df)} 个测试结果")
print(f"配置: {len(config_groups)} 种不同配置")

# 创建配置标签
config_groups['config_label'] = config_groups.apply(
    lambda row: f"{int(row['batch_size'])} records\n{int(row['station_count'])} stations",
    axis=1
)

# 创建图表
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Azure Functions Serverless Workflow - Performance Analysis', fontsize=16, fontweight='bold')

# 图表 1: 总执行时间 vs 负载
ax1 = axes[0, 0]
x_pos = np.arange(len(config_groups))
bars1 = ax1.bar(x_pos, config_groups['total_duration_sec'], color='steelblue', alpha=0.8)
ax1.set_xlabel('Configuration (Batch Size / Station Count)', fontweight='bold')
ax1.set_ylabel('Average Total Duration (seconds)', fontweight='bold')
ax1.set_title('Total Execution Time vs Load', fontweight='bold')
ax1.set_xticks(x_pos)
ax1.set_xticklabels(config_groups['config_label'], fontsize=9)
ax1.grid(axis='y', alpha=0.3)

# 添加数值标签
for bar in bars1:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.1f}s',
             ha='center', va='bottom', fontsize=9)

# 图表 2: 吞吐量 vs 负载
ax2 = axes[0, 1]
bars2 = ax2.bar(x_pos, config_groups['throughput_records_per_sec'], color='forestgreen', alpha=0.8)
ax2.set_xlabel('Configuration (Batch Size / Station Count)', fontweight='bold')
ax2.set_ylabel('Throughput (records/second)', fontweight='bold')
ax2.set_title('System Throughput vs Load', fontweight='bold')
ax2.set_xticks(x_pos)
ax2.set_xticklabels(config_groups['config_label'], fontsize=9)
ax2.grid(axis='y', alpha=0.3)

# 添加数值标签
for bar in bars2:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.2f}',
             ha='center', va='bottom', fontsize=9)

# 图表 3: 函数执行时间分解
ax3 = axes[1, 0]
width = 0.35
x = np.arange(len(config_groups))
bars3a = ax3.bar(x - width/2, config_groups['gen_duration_sec'], width,
                 label='GenerateAirQualityData', color='coral', alpha=0.8)
bars3b = ax3.bar(x + width/2, config_groups['proc_duration_sec'], width,
                 label='ProcessAirQualitySummary', color='skyblue', alpha=0.8)
ax3.set_xlabel('Configuration (Batch Size / Station Count)', fontweight='bold')
ax3.set_ylabel('Average Duration (seconds)', fontweight='bold')
ax3.set_title('Function Execution Time Breakdown', fontweight='bold')
ax3.set_xticks(x)
ax3.set_xticklabels(config_groups['config_label'], fontsize=9)
ax3.legend()
ax3.grid(axis='y', alpha=0.3)

# 图表 4: 峰值内存使用
ax4 = axes[1, 1]
bars4a = ax4.bar(x - width/2, config_groups['gen_peak_memory_mb'], width,
                 label='GenerateAirQualityData', color='mediumpurple', alpha=0.8)
bars4b = ax4.bar(x + width/2, config_groups['proc_peak_memory_mb'], width,
                 label='ProcessAirQualitySummary', color='lightcoral', alpha=0.8)
ax4.set_xlabel('Configuration (Batch Size / Station Count)', fontweight='bold')
ax4.set_ylabel('Peak Memory Usage (MB)', fontweight='bold')
ax4.set_title('Memory Consumption', fontweight='bold')
ax4.set_xticks(x)
ax4.set_xticklabels(config_groups['config_label'], fontsize=9)
ax4.legend()
ax4.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('performance_charts.png', dpi=300, bbox_inches='tight')
print("✓ 图表已保存: performance_charts.png")

# 创建第二组图表：可扩展性分析
fig2, axes2 = plt.subplots(1, 2, figsize=(14, 5))
fig2.suptitle('Scalability Analysis', fontsize=16, fontweight='bold')

# 图表 5: 负载 vs 执行时间（折线图）
ax5 = axes2[0]
batch_sizes = config_groups['batch_size'].values
total_times = config_groups['total_duration_sec'].values
ax5.plot(batch_sizes, total_times, marker='o', linewidth=2, markersize=8, color='steelblue')
ax5.set_xlabel('Batch Size (records)', fontweight='bold')
ax5.set_ylabel('Total Execution Time (seconds)', fontweight='bold')
ax5.set_title('Load vs Execution Time', fontweight='bold')
ax5.grid(True, alpha=0.3)

# 添加数据点标签
for i, (x, y) in enumerate(zip(batch_sizes, total_times)):
    ax5.annotate(f'{y:.1f}s', (x, y), textcoords="offset points",
                xytext=(0,10), ha='center', fontsize=9)

# 图表 6: 可扩展性效率
ax6 = axes2[1]
scalability_data = []
for i in range(len(config_groups) - 1):
    load_inc = ((config_groups.iloc[i+1]['batch_size'] / config_groups.iloc[i]['batch_size']) - 1) * 100
    time_inc = ((config_groups.iloc[i+1]['total_duration_sec'] / config_groups.iloc[i]['total_duration_sec']) - 1) * 100
    efficiency = (load_inc / time_inc) * 100 if time_inc > 0 else 0
    scalability_data.append({
        'transition': f"{int(config_groups.iloc[i]['batch_size'])}→{int(config_groups.iloc[i+1]['batch_size'])}",
        'load_increase': load_inc,
        'time_increase': time_inc,
        'efficiency': efficiency
    })

scalability_df = pd.DataFrame(scalability_data)
x_scale = np.arange(len(scalability_df))
width_scale = 0.35

bars6a = ax6.bar(x_scale - width_scale/2, scalability_df['load_increase'], width_scale,
                 label='Load Increase (%)', color='forestgreen', alpha=0.8)
bars6b = ax6.bar(x_scale + width_scale/2, scalability_df['time_increase'], width_scale,
                 label='Time Increase (%)', color='coral', alpha=0.8)
ax6.set_xlabel('Load Transition', fontweight='bold')
ax6.set_ylabel('Increase (%)', fontweight='bold')
ax6.set_title('Scalability Efficiency', fontweight='bold')
ax6.set_xticks(x_scale)
ax6.set_xticklabels(scalability_df['transition'])
ax6.legend()
ax6.grid(axis='y', alpha=0.3)

# 添加效率标注
for i, (bar1, bar2) in enumerate(zip(bars6a, bars6b)):
    load_val = bar1.get_height()
    time_val = bar2.get_height()
    efficiency = (load_val / time_val * 100) if time_val > 0 else 0
    status = "✓ Good" if efficiency > 100 else "⚠ Needs optimization"
    ax6.text(i, max(load_val, time_val) + 5, status, ha='center', fontsize=8, fontweight='bold')

plt.tight_layout()
plt.savefig('scalability_analysis.png', dpi=300, bbox_inches='tight')
print("✓ 可扩展性分析图表已保存: scalability_analysis.png")

print("\n✓✓✓ 所有图表生成完成！")
print("\n生成的文件:")
print("  - performance_charts.png (性能概览图表)")
print("  - scalability_analysis.png (可扩展性分析)")
