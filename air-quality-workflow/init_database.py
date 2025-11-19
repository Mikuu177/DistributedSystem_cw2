"""初始化 Azure SQL 数据库结构和 Change Tracking"""
import json
import os
import sys

from azure_sql import get_sql_connection


def execute_sql(cursor, sql, description):
    """执行 SQL 语句并处理错误"""
    print(f"  {description}...", end=" ")
    try:
        cursor.execute(sql)
        print("✓")
        return True
    except Exception as e:
        print(f"✗\n    错误: {e}")
        return False


def main():
    # 加载配置
    cfg = json.load(open("local.settings.json", encoding="utf-8"))
    os.environ.update(cfg["Values"])

    print("=" * 70)
    print("Azure SQL 数据库初始化")
    print("=" * 70)
    print()

    try:
        # 1. 启用数据库级别的 Change Tracking (需要单独连接，不能在事务中)
        print("【1/5】启用数据库 Change Tracking")
        conn = get_sql_connection()
        conn.autocommit = True  # ALTER DATABASE 必须在 autocommit 模式下
        with conn.cursor() as cursor:
            execute_sql(
                cursor,
                """
                ALTER DATABASE CURRENT
                SET CHANGE_TRACKING = ON
                (CHANGE_RETENTION = 2 DAYS, AUTO_CLEANUP = ON)
                """,
                "配置 Change Tracking（保留 2 天）"
            )
        conn.close()

        # 重新连接用于后续操作
        conn = get_sql_connection()
        print("✓ 已连接到数据库\n")

        with conn.cursor() as cursor:

            # 2. 创建主数据表 air_quality_data
            print("\n【2/5】创建 air_quality_data 表")
            execute_sql(
                cursor,
                """
                CREATE TABLE air_quality_data (
                    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                    station_id NVARCHAR(50),
                    recorded_at DATETIME2,
                    pm25 FLOAT,
                    pm10 FLOAT,
                    o3 FLOAT,
                    aqi INT
                )
                """,
                "创建空气质量数据表"
            )
            conn.commit()

            # 3. 创建汇总表 air_quality_summary
            print("\n【3/5】创建 air_quality_summary 表")
            execute_sql(
                cursor,
                """
                CREATE TABLE air_quality_summary (
                    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                    window_start DATETIME2,
                    window_end DATETIME2,
                    avg_aqi FLOAT,
                    max_pm25 FLOAT,
                    min_o3 FLOAT,
                    record_count INT
                )
                """,
                "创建统计汇总表"
            )
            conn.commit()

            # 4. 创建同步状态表 air_quality_sync_state
            print("\n【4/5】创建 air_quality_sync_state 表")
            execute_sql(
                cursor,
                """
                CREATE TABLE air_quality_sync_state (
                    id INT PRIMARY KEY CHECK (id = 1),
                    last_version BIGINT
                )
                """,
                "创建同步状态表"
            )
            execute_sql(
                cursor,
                "INSERT INTO air_quality_sync_state (id, last_version) VALUES (1, 0)",
                "初始化同步版本为 0"
            )
            conn.commit()

            # 5. 在 air_quality_data 表上启用 Change Tracking
            print("\n【5/5】启用表级别 Change Tracking")
            execute_sql(
                cursor,
                """
                ALTER TABLE air_quality_data
                ENABLE CHANGE_TRACKING
                WITH (TRACK_COLUMNS_UPDATED = OFF)
                """,
                "在 air_quality_data 表启用变更跟踪"
            )
            conn.commit()

            # 验证结果
            print("\n" + "=" * 70)
            print("验证数据库结构")
            print("=" * 70)

            cursor.execute("SELECT name FROM sys.tables ORDER BY name")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"\n已创建的表 ({len(tables)} 个):")
            for table in tables:
                print(f"  ✓ {table}")

            cursor.execute("SELECT COUNT(*) FROM air_quality_sync_state")
            count = cursor.fetchone()[0]
            print(f"\n同步状态初始化: {count} 条记录")

            cursor.execute("SELECT CHANGE_TRACKING_CURRENT_VERSION()")
            version = cursor.fetchone()[0]
            print(f"当前 Change Tracking 版本: {version}")

        conn.close()

        print("\n" + "=" * 70)
        print("✓✓✓ 数据库初始化完成！✓✓✓")
        print("=" * 70)

    except Exception as e:
        print(f"\n✗ 初始化失败: {type(e).__name__}")
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
