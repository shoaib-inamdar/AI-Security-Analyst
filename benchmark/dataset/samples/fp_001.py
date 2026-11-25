"""
BENCHMARK SAMPLE: fp_001
Type: SAFE CODE — Should NOT be flagged
This tests whether our scanner raises FALSE POSITIVES on safe code.
"""
import sqlite3

def get_user_safe(username:str):
    conn=sqlite3.connect("users.db")
    # SAFE: parameterized query — user input never touches the query string
    query="SELECT * FROM users WHERE username = ?"
    return conn.execute(query,(username)).fetchall()