"""A clean Python module."""



def greet(name: str, greeting: str | None = None) -> str:
    """Greet someone by name."""
    if greeting is None:
        greeting = "Hello"
    return f"{greeting}, {name}!"


def process_items(items: list[str]) -> str:
    """Join items into a comma-separated string."""
    return ", ".join(items)


if __name__ == "__main__":
    print(greet("World"))
    print(process_items(["a", "b", "c"]))
