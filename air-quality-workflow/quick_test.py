"""快速测试 Azure SQL 连接（使用缓存的 token）"""
import json
import os
import sys

# 加载配置
cfg = json.load(open("local.settings.json", encoding="utf-8"))
os.environ.update(cfg["Values"])

print("正在连接 Azure SQL...")
print(f"服务器: sc22wncw2.database.windows.net")
print(f"数据库: airquality_CW2")
print(f"认证: Azure AD (使用缓存的 token)\n")

try:
    from azure_sql import get_sql_connection

    conn = get_sql_connection()
    print("✓ 连接成功！\n")

    with conn.cursor() as cur:
        # 查询当前用户
        cur.execute("SELECT CURRENT_USER")
        user = cur.fetchone()[0]
        print(f"当前用户: {user}")

        # 列出表
        cur.execute("SELECT name FROM sys.tables ORDER BY name")
        tables = cur.fetchall()
        print(f"\n数据库中的表 ({len(tables)} 个):")
        if tables:
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("  (还没有表)")

    conn.close()
    print("\n✓✓✓ 连接测试成功！✓✓✓")

except Exception as e:
    print(f"✗ 连接失败: {type(e).__name__}")
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
