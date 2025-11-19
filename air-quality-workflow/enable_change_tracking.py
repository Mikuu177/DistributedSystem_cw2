"""启用 Azure SQL Change Tracking"""
import json
import os
import sys

from azure_sql import get_sql_connection


def main():
    # 加载配置
    cfg = json.load(open("local.settings.json", encoding="utf-8"))
    os.environ.update(cfg["Values"])

    print("=" * 70)
    print("启用 Change Tracking")
    print("=" * 70)
    print()

    try:
        # 1. 启用数据库级别的 Change Tracking
        print("【1/2】启用数据库级别 Change Tracking")
        conn = get_sql_connection()
        conn.autocommit = True  # ALTER DATABASE 必须在 autocommit 模式下

        with conn.cursor() as cursor:
            print("  配置 Change Tracking（保留 2 天）...", end=" ")
            try:
                cursor.execute("""
                    ALTER DATABASE CURRENT
                    SET CHANGE_TRACKING = ON
                    (CHANGE_RETENTION = 2 DAYS, AUTO_CLEANUP = ON)
                """)
                print("✓")
            except Exception as e:
                if "already enabled" in str(e) or "1712" in str(e):
                    print("✓ (已启用)")
                else:
                    print(f"✗\n    错误: {e}")
                    raise

        conn.close()

        # 2. 启用表级别的 Change Tracking
        print("\n【2/2】启用表级别 Change Tracking")
        conn = get_sql_connection()
        conn.autocommit = True

        with conn.cursor() as cursor:
            print("  在 air_quality_data 表启用变更跟踪...", end=" ")
            try:
                cursor.execute("""
                    ALTER TABLE air_quality_data
                    ENABLE CHANGE_TRACKING
                    WITH (TRACK_COLUMNS_UPDATED = OFF)
                """)
                print("✓")
            except Exception as e:
                if "already enabled" in str(e) or "4997" in str(e):
                    print("✓ (已启用)")
                else:
                    print(f"✗\n    错误: {e}")
                    raise

        # 3. 验证
        print("\n" + "=" * 70)
        print("验证 Change Tracking 状态")
        print("=" * 70)

        conn.autocommit = False
        with conn.cursor() as cursor:
            # 检查数据库级别
            cursor.execute("""
                SELECT is_change_tracking_enabled
                FROM sys.databases
                WHERE database_id = DB_ID()
            """)
            db_enabled = cursor.fetchone()[0]
            print(f"\n数据库 Change Tracking: {'✓ 已启用' if db_enabled else '✗ 未启用'}")

            # 检查表级别
            cursor.execute("""
                SELECT is_tracked
                FROM sys.change_tracking_tables
                WHERE object_id = OBJECT_ID('air_quality_data')
            """)
            row = cursor.fetchone()
            table_enabled = row[0] if row else False
            print(f"表 air_quality_data Change Tracking: {'✓ 已启用' if table_enabled else '✗ 未启用'}")

            # 获取当前版本
            cursor.execute("SELECT CHANGE_TRACKING_CURRENT_VERSION()")
            version = cursor.fetchone()[0]
            print(f"当前 Change Tracking 版本: {version if version else 0}")

        conn.close()

        print("\n" + "=" * 70)
        print("✓✓✓ Change Tracking 配置完成！✓✓✓")
        print("=" * 70)

    except Exception as e:
        print(f"\n✗ 配置失败: {type(e).__name__}")
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
