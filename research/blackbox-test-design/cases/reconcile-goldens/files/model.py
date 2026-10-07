"""Executable spec of the legacy loyalty-points service (Java 8, Spring; source held by the vendor).

points(order) must return what POST /points returns on the legacy stand. DECISIONS.md lists each rule and the goldens
it came from.
"""
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR

BASE_RATE = Decimal("0.05")

# D4: member codes in these regions are normalized by stripping leading zeros (goldens r3-07, r5-14, r8-02, r10-11).
STRIP_ZEROS_REGIONS = ("NL", "BE", "LU")

# D6: these tiers earn double points (goldens r2-01, r4-09).
DOUBLE_TIERS = ("GOLD", "PLATINUM")

# D9: in these regions the points are rounded up instead of down (goldens r7-03, r9-15).
ROUND_UP_REGIONS = ("PT", "GR")

KNOWN_MEMBERS = {
    "1234": "GOLD",
    "778": "SILVER",
    "0A12": "PLATINUM",
    "A0012": "SILVER",
}


def member_key(region: str, code: str) -> str:
    code = code.strip()
    if region in STRIP_ZEROS_REGIONS:
        code = code.lstrip("0") or "0"
    return code


def points(order: dict) -> dict:
    region = order["region"]
    key = member_key(region, order["memberCode"])
    tier = KNOWN_MEMBERS.get(key)
    if tier is None:
        return {"status": "UNKNOWN_MEMBER", "points": 0}
    raw = Decimal(str(order["amount"])) * BASE_RATE
    if tier in DOUBLE_TIERS:
        raw *= 2
    rounding = ROUND_CEILING if region in ROUND_UP_REGIONS else ROUND_FLOOR
    value = int(raw.to_integral_value(rounding=rounding))
    return {"status": "OK", "tier": tier, "points": value}
