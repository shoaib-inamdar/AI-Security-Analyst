"""
BENCHMARK SAMPLE: path_traversal_001
Type: Path Traversal (CWE-22) | Severity: HIGH
INTENTIONALLY VULNERABLE — For testing only.
"""
import os 

UPLOAD_DIR="/var/uploads"

def read_user_file(filename:str)->str:
    # VULNERABLE: user controls filename, no validation
    full_path=os.path.join(UPLOAD_DIR,filename)
    with open(full_path,"r")as f:
        return f.read()