def pytest_pycollect_makeitem(collector, name, obj):
    if isinstance(obj, type) and name.startswith("Test") and getattr(obj, "__module__", None) != collector.module.__name__:
        return []
    return None
