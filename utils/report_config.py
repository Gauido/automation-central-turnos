import os


REPORT_MODE = os.getenv("REPORT_MODE", "normal").lower()
ATTACH_TEST_CONTEXT = os.getenv("ATTACH_TEST_CONTEXT", "true").lower()


def is_debug_report() -> bool:
    return REPORT_MODE in ("debug", "diagnostics", "discovery", "full")


def is_normal_report() -> bool:
    return not is_debug_report()


def should_attach_test_context() -> bool:
    return ATTACH_TEST_CONTEXT in ("1", "true", "yes", "y", "on")
