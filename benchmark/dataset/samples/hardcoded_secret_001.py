"""
BENCHMARK SAMPLE: hardcoded_secret_001
Type: Hardcoded Credentials (CWE-798) | Severity: CRITICAL
INTENTIONALLY VULNERABLE — For testing only.
"""
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
DATABASE_PASSWORD = "SuperSecret123!"

def connect_to_aws():
    import boto3
    return boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )