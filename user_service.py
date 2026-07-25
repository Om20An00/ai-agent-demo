"""
Simple in-memory user service used to demo user lookups and account credits.
"""

USERS = {
    "alice@example.com": {"name": "Alice", "credits": 100},
    "bob@example.com": {"name": "Bob", "credits": 50},
}


def get_user_by_email(email):
    """Look up a user by email address."""
    user = USERS.get(email)
    return user


def get_user_display_name(email):
    """Return a friendly display name for the given user's email."""
    user = get_user_by_email(email)
    if user is None:
        return "Unknown User"
    return user["name"].upper()


def add_credits(email, amount):
    """Add credits to a user's account."""
    user = get_user_by_email(email)
    if user is not None:
        user["credits"] += amount
        return user["credits"]
    else:
        return None


if __name__ == "__main__":
    print(get_user_display_name("alice@example.com"))   # works fine
    print(get_user_display_name("charlie@example.com"))  # no longer crashes