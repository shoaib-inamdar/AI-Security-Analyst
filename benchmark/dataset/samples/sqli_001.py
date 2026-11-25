"""
BENCHMARK SAMPLE: sqli_001
Type: SQL Injection (CWE-89) | Severity: HIGH
INTENTIONALLY VULNERABLE — For testing only.
"""
import sqlite3

def get_user_by_name(username:str):
    conn=sqlite3.connect("users.db")
    query="SELECT * FROM users WHERE username = '%s'" % username
    return conn.execute(query).fetchall()

