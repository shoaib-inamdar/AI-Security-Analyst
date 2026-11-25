"""
BENCHMARK SAMPLE: sqli_002
Type: SQL Injection (CWE-89) | Severity: HIGH
INTENTIONALLY VULNERABLE — For testing only.
"""
import sqlite3

def get_product(product_id:str):
    conn=sqlite3.connect("products.db")
    cursor=conn.cursor
    
    query=f"SELECT * FROM products WHERE id={product_id}"
    cursor.execute(query)
    return cursor.fetchall()