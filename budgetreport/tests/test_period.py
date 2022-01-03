# test_period.py
from datetime import datetime as dt
from budgetreport import period

def test_periodStart():
    assert period.Period("year").getPeriodStart(dt(2021, 1, 1)) == dt(2021, 1, 1).date()
    assert period.Period("year").getPeriodStart(dt(2021, 6, 3)) == dt(2021, 1, 1).date()
    assert period.Period("year").getPeriodStart(dt(2021, 12, 31)) == dt(2021, 1, 1).date()
    assert period.Period("month").getPeriodStart(dt(2021, 3, 1)) == dt(2021, 3, 1).date()
    assert period.Period("month").getPeriodStart(dt(2021, 3, 15)) == dt(2021, 3, 1).date()
    assert period.Period("month").getPeriodStart(dt(2021, 3, 31)) == dt(2021, 3, 1).date()
    assert period.Period("biannual").getPeriodStart(dt(2021, 1, 1)) == dt(2021, 1, 1).date()
    assert period.Period("biannual").getPeriodStart(dt(2021, 4, 3)) == dt(2021, 1, 1).date()
    assert period.Period("biannual").getPeriodStart(dt(2021, 6, 30)) == dt(2021, 1, 1).date()
    assert period.Period("biannual").getPeriodStart(dt(2021, 7, 1)) == dt(2021, 7, 1).date()
    assert period.Period("biannual").getPeriodStart(dt(2021, 9, 12)) == dt(2021, 7, 1).date()
    assert period.Period("biannual").getPeriodStart(dt(2021, 12, 31)) == dt(2021, 7, 1).date()
    assert period.Period("week").getPeriodStart(dt(2021, 3, 3)) == dt(2021, 3, 1).date()
    assert period.Period("week").getPeriodStart(dt(2021, 3, 8)) == dt(2021, 3, 8).date()
    assert period.Period("week").getPeriodStart(dt(2021, 3, 20)) == dt(2021, 3, 15).date()
    assert period.Period("week").getPeriodStart(dt(2021, 3, 28)) == dt(2021, 3, 22).date()
    assert period.Period("day").getPeriodStart(dt(2021, 3, 3)) == dt(2021, 3, 3).date()

def test_periodEnd():
    assert period.Period("year").getPeriodEnd(dt(2021, 1, 1)) == dt(2021, 12, 31).date()
    assert period.Period("year").getPeriodEnd(dt(2021, 6, 3)) == dt(2021, 12, 31).date()
    assert period.Period("year").getPeriodEnd(dt(2021, 12, 31)) == dt(2021, 12, 31).date()
    assert period.Period("month").getPeriodEnd(dt(2021, 3, 1)) == dt(2021, 3, 31).date()
    assert period.Period("month").getPeriodEnd(dt(2021, 3, 15)) == dt(2021, 3, 31).date()
    assert period.Period("month").getPeriodEnd(dt(2021, 3, 31)) == dt(2021, 3, 31).date()
    assert period.Period("biannual").getPeriodEnd(dt(2021, 1, 1)) == dt(2021, 6, 30).date()
    assert period.Period("biannual").getPeriodEnd(dt(2021, 4, 3)) == dt(2021, 6, 30).date()
    assert period.Period("biannual").getPeriodEnd(dt(2021, 6, 30)) == dt(2021, 6, 30).date()
    assert period.Period("biannual").getPeriodEnd(dt(2021, 7, 1)) == dt(2021, 12, 31).date()
    assert period.Period("biannual").getPeriodEnd(dt(2021, 9, 12)) == dt(2021, 12, 31).date()
    assert period.Period("biannual").getPeriodEnd(dt(2021, 12, 31)) == dt(2021, 12, 31).date()
    assert period.Period("week").getPeriodEnd(dt(2021, 3, 3)) == dt(2021, 3, 7).date()
    assert period.Period("week").getPeriodEnd(dt(2021, 3, 8)) == dt(2021, 3, 14).date()
    assert period.Period("week").getPeriodEnd(dt(2021, 3, 20)) == dt(2021, 3, 21).date()
    assert period.Period("week").getPeriodEnd(dt(2021, 3, 28)) == dt(2021, 3, 31).date()
    assert period.Period("day").getPeriodEnd(dt(2021, 3, 3)) == dt(2021, 3, 3).date()
