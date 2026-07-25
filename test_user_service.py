from user_service import get_user_display_name

def test_known_user():
    assert get_user_display_name("alice@example.com") == "ALICE"

def test_unknown_user_does_not_crash():
    # Before the fix this raises AttributeError; after the fix it shouldn't crash
    result = get_user_display_name("charlie@example.com")
    assert isinstance(result, str)
