"""TEST-ONLY stub of the Engine track's calendars.py (CONTRACT.md names). Not shipped as app code."""
from dataclasses import dataclass
from datetime import date
NAME = {"gregorian": "Gregorian", "julian": "Julian", "revised_julian": "Revised Julian",
        "coptic": "Coptic", "ethiopian": "Ethiopian", "byzantine": "Byzantine"}
ERA = {"gregorian": "AD", "julian": "AD", "revised_julian": "AD", "coptic": "AM (Anno Martyrum)",
       "ethiopian": "Amete Mihret", "byzantine": "AM (Anno Mundi)"}

@dataclass
class CDate:
    year: int
    month: int
    day: int
    cal: str

def to_jdn(cal, y, m, d):
    import feasts
    return feasts.to_gregorian(cal, y, m, d).toordinal() + 1721425

def to_gregorian(cdate):
    import feasts
    return feasts.to_gregorian(cdate.cal, cdate.year, cdate.month, cdate.day)
