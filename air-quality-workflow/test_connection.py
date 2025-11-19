"""测试 Azure SQL 连接"""
import json
import os
import pyodbc

# 加载配置
cfg = json.load(open("local.settings.json", encoding="utf-8"))
os.environ.update(cfg["Values"])

conn_str = os.environ["SQL_CONNECTION_STRING"]
print(f"连接字符串: {conn_str[:100]}...")  # 只显示前100个字符

try:
    print("\n正在连接到 Azure SQL...")
    conn = pyodbc.connect(conn_str, timeout=30)
    print("✓ 连接成功！")

    # 测试查询
    with conn.cursor() as cur:
        cur.execute("SELECT @@VERSION")
        version = cur.fetchone()[0]
        print(f"\n数据库版本: {version[:80]}...")

        # 列出表
        cur.execute("SELECT name FROM sys.tables ORDER BY name")
        tables = cur.fetchall()
        print(f"\n数据库中的表 ({len(tables)} 个):")
        for table in tables:
            print(f"  - {table[0]}")

    conn.close()
    print("\n✓ 测试完成！连接正常工作。")

except Exception as e:
    print(f"\n✗ 连接失败: {type(e).__name__}")
    print(f"错误信息: {e}")
    import traceback
    traceback.print_exc()
