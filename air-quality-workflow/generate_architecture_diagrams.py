"""
生成系统架构图和工作流程图
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import matplotlib.lines as mlines

# 设置字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def create_system_architecture():
    """创建系统架构图"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # 标题
    ax.text(7, 9.5, 'Air Quality Monitoring System Architecture',
            fontsize=18, fontweight='bold', ha='center')
    ax.text(7, 9.0, 'Azure Functions Serverless Workflow',
            fontsize=12, ha='center', style='italic', color='gray')

    # === Azure Functions Layer ===
    # Function 1: GenerateAirQualityData
    func1_box = FancyBboxPatch((0.5, 5.5), 5, 2.5,
                               boxstyle="round,pad=0.1",
                               edgecolor='#0078D4', facecolor='#E6F2FF', linewidth=2)
    ax.add_patch(func1_box)
    ax.text(3, 7.5, 'Azure Function 1', fontsize=11, fontweight='bold', ha='center')
    ax.text(3, 7.1, 'GenerateAirQualityData', fontsize=10, ha='center', style='italic')
    ax.text(3, 6.7, '• Timer Trigger (every 1 min)', fontsize=8, ha='center')
    ax.text(3, 6.4, '• Simulate IoT sensors', fontsize=8, ha='center')
    ax.text(3, 6.1, '• Generate PM2.5, PM10, O3, AQI', fontsize=8, ha='center')
    ax.text(3, 5.8, '• Batch insert to database', fontsize=8, ha='center')

    # Function 2: ProcessAirQualitySummary
    func2_box = FancyBboxPatch((8.5, 5.5), 5, 2.5,
                               boxstyle="round,pad=0.1",
                               edgecolor='#0078D4', facecolor='#E6F2FF', linewidth=2)
    ax.add_patch(func2_box)
    ax.text(11, 7.5, 'Azure Function 2', fontsize=11, fontweight='bold', ha='center')
    ax.text(11, 7.1, 'ProcessAirQualitySummary', fontsize=10, ha='center', style='italic')
    ax.text(11, 6.7, '• Timer Trigger (every 2 min)', fontsize=8, ha='center')
    ax.text(11, 6.4, '• Query Change Tracking', fontsize=8, ha='center')
    ax.text(11, 6.1, '• Calculate statistics', fontsize=8, ha='center')
    ax.text(11, 5.8, '• Write summary', fontsize=8, ha='center')

    # === Azure SQL Database ===
    db_box = FancyBboxPatch((3.5, 2), 7, 2.5,
                            boxstyle="round,pad=0.15",
                            edgecolor='#D13438', facecolor='#FFE6E6', linewidth=2.5)
    ax.add_patch(db_box)
    ax.text(7, 4.0, 'Azure SQL Database', fontsize=12, fontweight='bold', ha='center')

    # Tables
    table1 = FancyBboxPatch((4, 2.5), 2.2, 1.2, boxstyle="round,pad=0.05",
                            edgecolor='#666', facecolor='white', linewidth=1)
    ax.add_patch(table1)
    ax.text(5.1, 3.4, 'air_quality_data', fontsize=9, fontweight='bold', ha='center')
    ax.text(5.1, 3.1, 'id, station_id,', fontsize=7, ha='center')
    ax.text(5.1, 2.9, 'recorded_at,', fontsize=7, ha='center')
    ax.text(5.1, 2.7, 'pm25, pm10, o3, aqi', fontsize=7, ha='center')

    table2 = FancyBboxPatch((6.5, 2.5), 2.2, 1.2, boxstyle="round,pad=0.05",
                            edgecolor='#666', facecolor='white', linewidth=1)
    ax.add_patch(table2)
    ax.text(7.6, 3.4, 'air_quality_summary', fontsize=9, fontweight='bold', ha='center')
    ax.text(7.6, 3.1, 'window_start,', fontsize=7, ha='center')
    ax.text(7.6, 2.9, 'avg_aqi, max_pm25,', fontsize=7, ha='center')
    ax.text(7.6, 2.7, 'min_o3, record_count', fontsize=7, ha='center')

    table3 = FancyBboxPatch((9, 2.5), 1.5, 1.2, boxstyle="round,pad=0.05",
                            edgecolor='#666', facecolor='white', linewidth=1)
    ax.add_patch(table3)
    ax.text(9.75, 3.4, 'sync_state', fontsize=9, fontweight='bold', ha='center')
    ax.text(9.75, 3.0, 'last_version', fontsize=7, ha='center')

    # Change Tracking badge
    ct_circle = Circle((10.5, 3.8), 0.25, color='#FFD700', ec='#FFA500', linewidth=2)
    ax.add_patch(ct_circle)
    ax.text(10.5, 3.8, 'CT', fontsize=8, fontweight='bold', ha='center', va='center')
    ax.text(11.5, 3.8, 'Change\nTracking', fontsize=7, ha='left', va='center')

    # === Arrows ===
    # Function 1 to Database (Write)
    arrow1 = FancyArrowPatch((3, 5.5), (5.1, 4.5),
                            arrowstyle='->', mutation_scale=20, linewidth=2,
                            color='#107C10')
    ax.add_patch(arrow1)
    ax.text(3.5, 5.2, 'INSERT', fontsize=8, color='#107C10', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#107C10'))

    # Database to Function 2 (Change Tracking)
    arrow2 = FancyArrowPatch((9.75, 4.5), (11, 5.5),
                            arrowstyle='->', mutation_scale=20, linewidth=2,
                            color='#0078D4', linestyle='dashed')
    ax.add_patch(arrow2)
    ax.text(10.5, 5.2, 'CHANGES', fontsize=8, color='#0078D4', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#0078D4'))

    # Function 2 to Database (Write Summary)
    arrow3 = FancyArrowPatch((11, 5.5), (7.6, 4.5),
                            arrowstyle='->', mutation_scale=20, linewidth=2,
                            color='#8B5CF6')
    ax.add_patch(arrow3)
    ax.text(9, 5.0, 'AGGREGATE', fontsize=8, color='#8B5CF6', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#8B5CF6'))

    # === Timer Triggers ===
    # Timer 1
    timer1 = Circle((1, 6.75), 0.35, color='#FF6B35', ec='#C7522A', linewidth=2)
    ax.add_patch(timer1)
    ax.text(1, 6.75, '⏰', fontsize=14, ha='center', va='center')
    timer1_arrow = FancyArrowPatch((1.35, 6.75), (2.3, 6.75),
                                  arrowstyle='->', mutation_scale=15, linewidth=1.5,
                                  color='#FF6B35')
    ax.add_patch(timer1_arrow)
    ax.text(1, 6.3, 'Every 1 min', fontsize=7, ha='center')

    # Timer 2
    timer2 = Circle((13, 6.75), 0.35, color='#FF6B35', ec='#C7522A', linewidth=2)
    ax.add_patch(timer2)
    ax.text(13, 6.75, '⏰', fontsize=14, ha='center', va='center')
    timer2_arrow = FancyArrowPatch((12.65, 6.75), (11.7, 6.75),
                                  arrowstyle='->', mutation_scale=15, linewidth=1.5,
                                  color='#FF6B35')
    ax.add_patch(timer2_arrow)
    ax.text(13, 6.3, 'Every 2 min', fontsize=7, ha='center')

    # === IoT Sensors (Input) ===
    sensor_y = 8.3
    for i, x_pos in enumerate([0.8, 1.8, 2.8]):
        sensor = FancyBboxPatch((x_pos, sensor_y), 0.6, 0.4,
                               boxstyle="round,pad=0.05",
                               edgecolor='#34A853', facecolor='#D4F4DD', linewidth=1.5)
        ax.add_patch(sensor)
        ax.text(x_pos + 0.3, sensor_y + 0.2, f'S{i+1}', fontsize=7, ha='center', fontweight='bold')

    ax.text(2, 8.9, 'IoT Sensors (Simulated)', fontsize=8, ha='center', style='italic')

    # Arrow from sensors to Function 1
    sensor_arrow = FancyArrowPatch((2, 8.3), (2.5, 7.8),
                                  arrowstyle='->', mutation_scale=15, linewidth=1.5,
                                  color='#34A853', linestyle='dotted')
    ax.add_patch(sensor_arrow)

    # === Legend ===
    legend_y = 0.8
    ax.text(0.5, legend_y, 'Components:', fontsize=9, fontweight='bold')

    # Legend items
    legend_items = [
        ('Azure Function', '#0078D4'),
        ('Azure SQL Database', '#D13438'),
        ('Timer Trigger', '#FF6B35'),
        ('Data Flow', '#107C10')
    ]

    for i, (label, color) in enumerate(legend_items):
        x = 0.5 + (i * 3.5)
        legend_box = FancyBboxPatch((x, 0.2), 0.3, 0.3,
                                   boxstyle="round,pad=0.02",
                                   edgecolor=color, facecolor='white', linewidth=1.5)
        ax.add_patch(legend_box)
        ax.text(x + 0.5, 0.35, label, fontsize=7, va='center')

    plt.tight_layout()
    plt.savefig('system_architecture.png', dpi=300, bbox_inches='tight')
    print("✓ 系统架构图已保存: system_architecture.png")
    plt.close()


def create_workflow_diagram():
    """创建工作流程图"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # 标题
    ax.text(6, 9.5, 'Serverless Workflow - Data Flow',
            fontsize=16, fontweight='bold', ha='center')

    # === Workflow Steps ===
    steps = [
        (6, 8.5, 'START\nTimer Trigger\n(Every 1 min)', '#FF6B35'),
        (6, 7.0, 'Function 1\nGenerate Data\n(BATCH_SIZE records)', '#0078D4'),
        (6, 5.5, 'Database Write\nINSERT into\nair_quality_data', '#107C10'),
        (6, 4.0, 'Change Tracking\nVersion++\nDetect Changes', '#FFD700'),
        (6, 2.5, 'Function 2\nProcess Changes\nCalculate Stats', '#8B5CF6'),
        (6, 1.0, 'Database Write\nINSERT into\nair_quality_summary', '#D13438'),
    ]

    for i, (x, y, text, color) in enumerate(steps):
        if i == 0:  # Start - circle
            circle = Circle((x, y), 0.4, color=color, ec='black', linewidth=2)
            ax.add_patch(circle)
            ax.text(x, y, text, fontsize=8, ha='center', va='center',
                   fontweight='bold', color='white')
        else:  # Other steps - rectangles
            box = FancyBboxPatch((x-1.2, y-0.4), 2.4, 0.8,
                                boxstyle="round,pad=0.1",
                                edgecolor='black', facecolor=color,
                                linewidth=2, alpha=0.3)
            ax.add_patch(box)
            ax.text(x, y, text, fontsize=9, ha='center', va='center',
                   fontweight='bold')

        # Arrow to next step
        if i < len(steps) - 1:
            arrow = FancyArrowPatch((x, y - 0.5), (x, steps[i+1][1] + 0.5),
                                   arrowstyle='->', mutation_scale=20,
                                   linewidth=2.5, color='black')
            ax.add_patch(arrow)

    # === Side annotations ===
    # Left side - timing
    ax.text(2, 7.0, 'Data\nGeneration\nPhase', fontsize=9, ha='center',
           style='italic', color='#0078D4',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='#E6F2FF', edgecolor='#0078D4'))

    ax.text(2, 2.5, 'Aggregation\nPhase', fontsize=9, ha='center',
           style='italic', color='#8B5CF6',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='#F3E8FF', edgecolor='#8B5CF6'))

    # Right side - metrics
    metrics_x = 9.5
    ax.text(metrics_x, 7.0, 'Performance:', fontsize=8, fontweight='bold')
    ax.text(metrics_x, 6.6, '• 8-62s (depends on batch)', fontsize=7)
    ax.text(metrics_x, 6.3, '• 2-3 rec/sec throughput', fontsize=7)
    ax.text(metrics_x, 6.0, '• <0.1MB memory', fontsize=7)

    ax.text(metrics_x, 2.5, 'Change Tracking:', fontsize=8, fontweight='bold')
    ax.text(metrics_x, 2.1, '• Incremental updates', fontsize=7)
    ax.text(metrics_x, 1.8, '• Version-based sync', fontsize=7)
    ax.text(metrics_x, 1.5, '• 4-6s processing', fontsize=7)

    # === Loop back ===
    loop_arrow = FancyArrowPatch((7.5, 0.6), (7.5, 0.3),
                                arrowstyle='->', mutation_scale=15,
                                linewidth=2, color='gray', linestyle='dashed')
    ax.add_patch(loop_arrow)

    loop_arrow2 = FancyArrowPatch((7.5, 0.3), (9, 0.3),
                                 arrowstyle='-', mutation_scale=15,
                                 linewidth=2, color='gray', linestyle='dashed')
    ax.add_patch(loop_arrow2)

    loop_arrow3 = FancyArrowPatch((9, 0.3), (9, 8.5),
                                 arrowstyle='-', mutation_scale=15,
                                 linewidth=2, color='gray', linestyle='dashed')
    ax.add_patch(loop_arrow3)

    loop_arrow4 = FancyArrowPatch((9, 8.5), (6.5, 8.5),
                                 arrowstyle='->', mutation_scale=15,
                                 linewidth=2, color='gray', linestyle='dashed')
    ax.add_patch(loop_arrow4)

    ax.text(9.2, 4.5, 'Continuous\nWorkflow\nLoop', fontsize=8, ha='center',
           rotation=90, color='gray', style='italic')

    plt.tight_layout()
    plt.savefig('workflow_diagram.png', dpi=300, bbox_inches='tight')
    print("✓ 工作流程图已保存: workflow_diagram.png")
    plt.close()


def main():
    print("生成架构图和流程图...\n")
    create_system_architecture()
    create_workflow_diagram()
    print("\n✓✓✓ 所有图表生成完成！")
    print("\n生成的文件:")
    print("  - system_architecture.png (系统架构图)")
    print("  - workflow_diagram.png (工作流程图)")


if __name__ == "__main__":
    main()
