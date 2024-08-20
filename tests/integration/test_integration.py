from main import greet_user


def test_greet_user():
    assert greet_user("Alice") == "Hello, World! Alice!"
    assert greet_user("Bob") == "Hello, World! Bob!"
