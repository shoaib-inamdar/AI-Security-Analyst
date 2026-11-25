"""
BENCHMARK SAMPLE: command_injection_001
Type: Command Injection (CWE-78) | Severity: CRITICAL
INTENTIONALLY VULNERABLE — For testing only.
"""
import os

def ping_host(hostname:str)->str:
    # VULNERABLE: hostname injected directly into shell command
    result=os.system(f"ping -c 4 {hostname}")
    return str(result)