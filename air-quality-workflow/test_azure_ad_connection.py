"""测试使用 Azure AD 用户名密码连接 Azure SQL"""
import json
import os
import sys

# 加载配置
cfg = json.load(open("local.settings.json", encoding="utf-8"))
os.environ.update(cfg["Values"])

# 设置 ODBC 配置路径（macOS 需要）
os.environ["ODBCSYSINI"] = "/opt/homebrew/etc"

print("配置信息:")
print(f"  服务器: sc22wncw2.database.windows.net")
print(f"  数据库: airquality_CW2")
print(f"  用户名: {os.environ.get('AZURE_SQL_USERNAME')}")
print(f"  认证方式: Azure AD (UsernamePasswordCredential)")
print()

try:
    # 导入 azure_sql 模块
    from azure_sql import get_sql_connection

    print("正在获取 Azure AD token...")
    conn = get_sql_connection()
    print("✓ 连接成功！")

    # 测试查询
    with conn.cursor() as cur:
        print("\n正在执行测试查询...")

        # 查询数据库版本
        cur.execute("SELECT @@VERSION")
        version = cur.fetchone()[0]
        print(f"\n数据库版本:")
        print(f"  {version[:80]}...")

        # 列出所有表
        cur.execute("SELECT name FROM sys.tables ORDER BY name")
        tables = cur.fetchall()
        print(f"\n数据库中的表 ({len(tables)} 个):")
        if tables:
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("  (数据库中还没有表)")

        # 查询当前用户
        cur.execute("SELECT CURRENT_USER")
        user = cur.fetchone()[0]
        print(f"\n当前登录用户: {user}")

    conn.close()
    print("\n✓✓✓ 测试完成！Azure SQL 连接正常工作！✓✓✓")

except Exception as e:
    print(f"\n✗ 连接失败: {type(e).__name__}")
    print(f"错误信息: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
