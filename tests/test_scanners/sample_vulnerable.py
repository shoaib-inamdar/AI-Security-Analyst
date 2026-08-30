"""
INTENTIONALLY VULNERABLE FILE — For scanner testing only.
Do NOT use any of these patterns in real code.
"""
import sqlite3
import hashlib


def get_user(username: str):
    """VULNERABLE: SQL Injection via string formatting."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # BAD: user input directly in query string
    query = "SELECT * FROM users WHERE username = '%s'" % username
    cursor.execute(query)
    return cursor.fetchall()


def hash_password(password: str) -> str:
    """VULNERABLE: MD5 is cryptographically broken."""
    return hashlib.md5(password.encode()).hexdigest()


# VULNERABLE: hardcoded secret
ADMIN_SECRET = "super_secret_admin_key_12345"
