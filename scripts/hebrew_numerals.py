"""Convert Hebrew alphabetic numerals (gematria) to integers.

Handles the forms used on chabadlibrary.org, e.g. "קסט", "טו", "א'רכד" (1224),
with optional geresh/gershayim marks and surrounding whitespace.
"""

VALUES = {
    "א": 1, "ב": 2, "ג": 3, "ד": 4, "ה": 5, "ו": 6, "ז": 7, "ח": 8, "ט": 9,
    "י": 10, "כ": 20, "ך": 20, "ל": 30, "מ": 40, "ם": 40, "נ": 50, "ן": 50,
    "ס": 60, "ע": 70, "פ": 80, "ף": 80, "צ": 90, "ץ": 90,
    "ק": 100, "ר": 200, "ש": 300, "ת": 400,
}
GERESH = "'׳’"
GERSHAYIM = '"״”'


def _sum(letters: str) -> int:
    return sum(VALUES[ch] for ch in letters)


def hebrew_to_int(text: str) -> int:
    """Parse a Hebrew numeral. Raises ValueError if it contains other characters."""
    s = text.strip()
    for ch in GERSHAYIM:
        s = s.replace(ch, "")
    # A geresh after the first group marks thousands: "א'רכד" -> 1*1000 + 224.
    for ch in GERESH:
        s = s.replace(ch, "'")
    parts = [p.strip() for p in s.split("'")]
    bad = [ch for p in parts for ch in p if ch not in VALUES]
    if bad or not any(parts):
        raise ValueError(f"not a Hebrew numeral: {text!r}")
    if len(parts) == 1 or (len(parts) == 2 and parts[1] == ""):
        return _sum(parts[0])
    if len(parts) == 2:
        return _sum(parts[0]) * 1000 + _sum(parts[1])
    raise ValueError(f"not a Hebrew numeral: {text!r}")


if __name__ == "__main__":
    for t, n in [("א", 1), ("טו", 15), ("קסט", 169), ("תשסו", 766),
                 ("א'רכד", 1224), ("ט'שעט ", 9379), ("י'תקנח", 10558), ('כ"ח', 28)]:
        assert hebrew_to_int(t) == n, (t, hebrew_to_int(t), n)
    print("ok")
