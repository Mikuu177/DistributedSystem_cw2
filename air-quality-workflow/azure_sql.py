"""Helpers for acquiring Azure SQL connections using Azure AD credentials."""

from __future__ import annotations

import os
import threading
from datetime import datetime, timedelta
from typing import Any, Dict

import pyodbc
from azure.identity import (
    DeviceCodeCredential,
    ManagedIdentityCredential,
    TokenCachePersistenceOptions,
)

_ODBC_TOKEN_KEY = 1256
_TOKEN_SCOPE = "https://database.windows.net/.default"
_TOKEN_REFRESH_MARGIN = timedelta(minutes=2)

_credential_lock = threading.Lock()
_credential = None
_token_cache: Dict[str, Any] = {"bytes": None, "expires_on": datetime.min}


def _build_credential():
    """Create a credential suitable for the current hosting environment."""
    global _credential  # pylint: disable=global-statement
    if _credential is not None:
        return _credential

    with _credential_lock:
        if _credential is not None:
            return _credential

        if os.environ.get("MSI_ENDPOINT") or os.environ.get("IDENTITY_ENDPOINT"):
            _credential = ManagedIdentityCredential()
        else:
            cache_opts = TokenCachePersistenceOptions(allow_unencrypted_storage=True)
            _credential = DeviceCodeCredential(
                client_id="04b07795-8ddb-461a-bbee-02f9e1bf7b46",
                cache_persistence_options=cache_opts,
            )
        return _credential


def _get_token_bytes() -> bytes:
    """Acquire (and cache) an access token for Azure SQL."""
    credential = _build_credential()
    now = datetime.utcnow()
    expires_on = _token_cache["expires_on"]
    if _token_cache["bytes"] and expires_on - now > _TOKEN_REFRESH_MARGIN:
        return _token_cache["bytes"]

    access_token = credential.get_token(_TOKEN_SCOPE)
    _token_cache["bytes"] = access_token.token.encode("utf-16-le")
    _token_cache["expires_on"] = datetime.utcfromtimestamp(access_token.expires_on)
    return _token_cache["bytes"]


def get_sql_connection():
    """Return a pyodbc connection, using Azure AD auth if no UID/PWD is supplied."""
    conn_str = os.environ["SQL_CONNECTION_STRING"]
    if "Uid=" in conn_str or "uid=" in conn_str:
        return pyodbc.connect(conn_str, timeout=30)
    token_bytes = _get_token_bytes()
    return pyodbc.connect(conn_str, attrs_before={_ODBC_TOKEN_KEY: token_bytes}, timeout=30)
