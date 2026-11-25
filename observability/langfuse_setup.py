"""
Configures Langfuse to trace all LangChain/LangGraph LLM calls.
Import and call setup_langfuse() once at application startup.

Usage in backend/main.py:
    from observability.langfuse_setup import setup_langfuse
    setup_langfuse()

Usage when making AI calls:
    from observability.langfuse_setup import get_handler
    result = chain.invoke(input, config={"callbacks": [get_handler()]})
"""

import os

try:
    from langfuse.callback import CallbackHandler as LangfuseCallbackHandler
    _LANGFUSE_AVAILABLE = True
except ImportError:
    try:
        from langfuse.langchain import CallbackHandler as LangfuseCallbackHandler
        _LANGFUSE_AVAILABLE = True
    except ImportError:
        LangfuseCallbackHandler = None  # type: ignore
        _LANGFUSE_AVAILABLE = False

_handler:LangfuseCallbackHandler | None=None

def setup_langfuse()-> LangfuseCallbackHandler | None:
    """Initialize Langfuse at app startup. Returns handler or None if not configured."""
    global _handler
    if not _LANGFUSE_AVAILABLE:
        print("⚠️  Langfuse package not available — LLM call logging disabled.")
        _handler = None
        return None
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key=os.getenv("LANGFUSE_SECRET_KEY")
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

    if not public_key or not secret_key:
        print("⚠️  Langfuse not configured — LLM call logging disabled.")

        _handler=None
        return None

    _handler=LangfuseCallbackHandler(
        public_key=public_key,
        secret_key=secret_key,
        host=host,
        trace_name="security-analysis",
    )
    print("✅ Langfuse LLM logging enabled.")
    return _handler

def get_handler()-> LangfuseCallbackHandler | None:
    """Get the singleton Langfuse handler (call setup_langfuse() first)."""
    return _handler