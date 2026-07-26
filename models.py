"""Shared data helpers used by user_service.py."""

def format_email(email):
    """Normalize an email address for lookups."""
    if email is None or email.strip() == "":
        return None
    return email.strip().lower()