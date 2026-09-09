"""Shared Supabase client for database operations.

Authentication and database requests need the same client so the active session
token is attached to row-level-security protected profile queries.
"""

from backend.src.auth import supabase
