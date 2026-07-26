"""Shared data helpers used by user_service.py."""

def format_email(email):
    """Normalize an email address for lookups."""
    return email.strip().lower()
