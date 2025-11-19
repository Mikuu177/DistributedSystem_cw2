"""Helpers for acquiring Azure SQL connections."""

import logging
import os
import re
import pyodbc

def get_sql_connection():
    """Return a pyodbc connection, correcting the driver name in the process."""
    conn_str = os.environ["SQL_CONNECTION_STRING"]

    # 强制修正驱动名称，以解决 Azure 配置缓存问题
    # 这个正则表达式会找到任何版本的 "ODBC Driver XX for SQL Server" 并将其替换为正确的版本 18
    corrected_conn_str, count = re.subn(
        r'Driver\s*=\s*\{ODBC Driver \d+ for SQL Server\}',
        'Driver={ODBC Driver 18 for SQL Server}',
        conn_str,
        flags=re.IGNORECASE
    )

    if count > 0:
        logging.info("Code-level fix: Corrected ODBC driver name to version 18.")
    else:
        logging.warning("Code-level fix: Driver specification not found in connection string. Using as is.")

    logging.info("Attempting connection with pyodbc...")
    return pyodbc.connect(corrected_conn_str, timeout=30)
