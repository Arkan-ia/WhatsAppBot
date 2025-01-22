import os
from typing import Any


def flexible_bind_wrapper(mock: Any, interface: Any, to: Any):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not mock or not interface or not to:
                raise Exception("Mock, interface and to must be provided")

            binder = args[1]
            if not binder:
                raise Exception("Binder must be provided")

            is_test = os.getenv("PYTHON_ENV") == "test"
            binder.bind(
                interface,
                to=(mock if is_test else to),
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator
