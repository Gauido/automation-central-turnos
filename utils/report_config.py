import os


REPORT_MODE = os.getenv("REPORT_MODE", "normal").lower()


def is_debug_report() -> bool:
    return REPORT_MODE in ("debug", "diagnostics", "discovery", "full")


def is_normal_report() -> bool:
    return not is_debug_report()
