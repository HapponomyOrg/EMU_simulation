from emusim.cockpit.utilities.cycles import Period, Interval


def test_period_completion():
    year: Period = Period(1, Interval.YEAR)
    month = Period(1, Interval.MONTH)
    week = Period(1, Interval.WEEK)

    assert year.period_complete(Period.YEAR_DAYS)
    assert month.period_complete(Period.MONTH_DAYS)
    assert week.period_complete(Period.WEEK_DAYS)

    assert year.period_complete(Period.YEAR_DAYS - 1)
    assert month.period_complete(Period.MONTH_DAYS - 1)
    assert week.period_complete(Period.WEEK_DAYS - 1)
