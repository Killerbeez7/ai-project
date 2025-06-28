from src.chains.greet import say_hello
def test_greeting_contains_name():
    assert "Alice" in say_hello("Alice")