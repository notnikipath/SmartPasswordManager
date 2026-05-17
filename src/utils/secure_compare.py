from __future__ import annotations

import hmac


def constant_time_equals(left: str, right: str) -> bool:
    return hmac.compare_digest(left, right)
