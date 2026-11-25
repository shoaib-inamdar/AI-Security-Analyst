"""
BENCHMARK SAMPLE: weak_crypto_001
Type: Weak Cryptographic Hash (CWE-327) | Severity: MEDIUM
INTENTIONALLY VULNERABLE — For testing only.
"""
import hashlib

def hash_password(password:str)->str:
    return hashlib.md5(password.encode()).hexdigest()

def verify_password(password:str,stored_hash:str)->bool:
    return hash_password(password)==stored_hash