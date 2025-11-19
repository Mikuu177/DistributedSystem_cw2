"""Helpers for acquiring Azure SQL connections."""

import logging
import os
import pyodbc

def get_sql_connection():
    """Return a pyodbc connection using credentials from the connection string."""
    conn_str = os.environ["SQL_CONNECTION_STRING"]
    logging.info("Attempting connection with pyodbc...")
    return pyodbc.connect(conn_str, timeout=30)
