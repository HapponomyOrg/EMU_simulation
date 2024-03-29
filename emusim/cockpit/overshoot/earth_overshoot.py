import calendar
from datetime import date

from dateutil import relativedelta


class Earth_Overshoot:
    START_DATE = date(1969, 12, 31)

    FIRST_YEAR = 1970
    LAST_YEAR = 2022

    overshoot_dates = {
        1970: date(1970, 12, 29),
        1971: date(1971, 12, 20),
        1972: date(1972, 12, 9),
        1973: date(1973, 11, 26),
        1974: date(1974, 11, 27),
        1975: date(1975, 11, 30),
        1976: date(1976, 11, 16),
        1977: date(1977, 11, 10),
        1978: date(1978, 11, 7),
        1979: date(1979, 10, 29),
        1980: date(1980, 11, 3),
        1981: date(1981, 11, 11),
        1982: date(1982, 11, 15),
        1983: date(1983, 11, 14),
        1984: date(1984, 11, 6),
        1985: date(1985, 11, 4),
        1986: date(1986, 10, 30),
        1987: date(1987, 10, 23),
        1988: date(1988, 10, 15),
        1989: date(1989, 10, 12),
        1990: date(1990, 10, 11),
        1991: date(1991, 10, 10),
        1992: date(1992, 10, 13),
        1993: date(1993, 10, 13),
        1994: date(1994, 10, 11),
        1995: date(1995, 10, 5),
        1996: date(1996, 10, 2),
        1997: date(1997, 9, 30),
        1998: date(1998, 9, 30),
        1999: date(1999, 9, 30),
        2000: date(2000, 9, 23),
        2001: date(2001, 9, 22),
        2002: date(2002, 9, 19),
        2003: date(2003, 9, 9),
        2004: date(2004, 9, 1),
        2005: date(2005, 8, 26),
        2006: date(2006, 8, 20),
        2007: date(2007, 8, 14),
        2008: date(2008, 8, 15),
        2009: date(2009, 8, 19),
        2010: date(2010, 8, 8),
        2011: date(2011, 8, 4),
        2012: date(2012, 8, 4),
        2013: date(2013, 8, 4),
        2014: date(2014, 8, 5),
        2015: date(2015, 8, 6),
        2016: date(2016, 8, 5),
        2017: date(2017, 8, 3),
        2018: date(2018, 8, 1),
        2019: date(2019, 7, 29),
        2020: date(2020, 8, 22),
        2021: date(2021, 7, 29),
        2022: date(2022, 7, 28)
    }

    overshoot_data = {}


    def __init__(self):
        cumulative_overshoot_date = self.START_DATE

        for year in sorted(self.overshoot_dates.keys()):
            overshoot_date = self.overshoot_dates[year]
            self.overshoot_data[overshoot_date.year] = Overshoot_Data(overshoot_date, cumulative_overshoot_date)
            cumulative_overshoot_date = self.overshoot_data[year].cumulative_overshoot_date


    def calculate_future_date(self, current_date):
        year = current_date.year
        extra_days = 0

        if year < self.FIRST_YEAR:
            return current_date
        else:
            cur_year = year

            while cur_year >= self.FIRST_YEAR:
                if cur_year > self.LAST_YEAR:
                    year_weight = self.overshoot_data[self.LAST_YEAR].weight
                else:
                    year_weight = self.overshoot_data[cur_year].weight

                if cur_year == year:
                    extra_days += current_date.timetuple().tm_yday * year_weight
                else:
                    if calendar.isleap(cur_year):
                        extra_days += 366 * year_weight
                    else:
                        extra_days += 365 * year_weight

                cur_year -= 1

            return self.START_DATE + relativedelta.relativedelta(days=round(extra_days + 0.5))


    def calculate_past_date(self, current_date):
        if current_date.year < self.FIRST_YEAR:
            return current_date
        else:
            approximation_date_found = False
            delta = current_date - date(1970, 1, 1)
            delta_days = round(delta.days / 2)
            past_date = date(1970, 1, 1) + relativedelta.relativedelta(days=delta_days)
            future_date = self.calculate_future_date(past_date)

            while not approximation_date_found and delta_days != 0:
                delta_days = delta_days / 2

                if future_date > current_date:
                    past_date -= relativedelta.relativedelta(days=delta_days)
                    future_date = self.calculate_future_date(past_date)
                elif future_date < current_date:
                    past_date += relativedelta.relativedelta(days=delta_days)
                    future_date = self.calculate_future_date(past_date)
                else:
                    approximation_date_found = True

            if current_date != future_date:
                while future_date > current_date:
                    past_date -= relativedelta.relativedelta(days=1)
                    future_date = self.calculate_future_date(past_date)

                while future_date < current_date:
                    past_date += relativedelta.relativedelta(days=1)
                    future_date = self.calculate_future_date(past_date)

            return past_date


class Overshoot_Data:

    def __init__(self, overshoot_date, cumulative_overshoot_date):
        self.overshoot_date = overshoot_date
        self.cumulative_overshoot_date = cumulative_overshoot_date

        self.year = overshoot_date.year

        if calendar.isleap(self.year):
            self.days_in_year = 366
        else:
            self.days_in_year = 365

        self.day_in_year = overshoot_date.timetuple().tm_yday
        self.days_left = self.days_in_year - self.day_in_year

        self.weight = self.days_in_year / self.day_in_year
        self.weighted_days_remaining = relativedelta.relativedelta(days=round(self.days_left * self.weight))

        self.overshoot = date(self.year, 12, 31) + self.weighted_days_remaining
        self.cumulative_overshoot_date += self.weighted_days_remaining + relativedelta.relativedelta(
            days=self.days_in_year)


    def get_overshoot_days(self):
        return round(self.days_in_year * self.weight - self.days_in_year)


    def get_cumulative_overshoot_days(self):
        d1 = date(self.year, 12, 31)
        d2 = self.cumulative_overshoot_date

        return abs((d2 - d1).days)
