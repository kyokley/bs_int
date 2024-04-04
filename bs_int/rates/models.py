import csv
import requests
import logging

from io import StringIO
from dateutil.parser import parse

from django.db import models
from django.utils import timezone

REQUEST_TIMEOUT = 60

CURRENT_MONTH_TREASURY_URL_TEMPLATE = 'https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/all/{year}{month}?type=daily_treasury_yield_curve&field_tdr_date_value_month={year}{month}&page&_format=csv'

ANNUAL_TREASURY_URL_TEMPLATE = 'https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{year}/all?type=daily_treasury_yield_curve&field_tdr_date_value={year}&page&_format=csv'

logger = logging.getLogger(__file__)


class TreasuryData(models.Model):
    _treasury_map = {'1 Mo': 'one_month',
                     '1 Yr': 'one_year',
                     '10 Yr': 'ten_year',
                     '2 Mo': 'two_month',
                     '2 Yr': 'two_year',
                     '20 Yr': 'twenty_year',
                     '3 Mo': 'three_month',
                     '3 Yr': 'three_year',
                     '30 Yr': 'thirty_year',
                     '4 Mo': 'four_month',
                     '5 Yr': 'five_year',
                     '6 Mo': 'six_month',
                     '7 Yr': 'seven_year',
                     }

    _maturity_order = ('six_month',
                       'one_year',
                       'two_year',
                       'three_year',
                       'five_year',
                       'seven_year',
                       'ten_year',
                       'twenty_year',
                       'thirty_year',
                       )

    date = models.DateField(null=False,
                            blank=False)

    one_month = models.FloatField(null=True, blank=False)
    two_month = models.FloatField(null=True, blank=False)
    three_month = models.FloatField(null=True, blank=False)
    four_month = models.FloatField(null=True, blank=False)
    six_month = models.FloatField(null=True, blank=False)

    one_year = models.FloatField(null=True, blank=False)
    two_year = models.FloatField(null=True, blank=False)
    three_year = models.FloatField(null=True, blank=False)
    five_year = models.FloatField(null=True, blank=False)
    seven_year = models.FloatField(null=True, blank=False)
    ten_year = models.FloatField(null=True, blank=False)
    twenty_year = models.FloatField(null=True, blank=False)
    thirty_year = models.FloatField(null=True, blank=False)

    class Meta:
        constraints = [
            models.UniqueConstraint('date', name='unique_date'),
        ]
        verbose_name_plural = 'Treasury Data'

    def __str__(self):
        return f'<{self.__class__.__name__} {self.date}>'

    def __repr__(self):
        return str(self)

    def _retrieve_treasury_data(self):
        current_date = timezone.now().date()

        if current_date.month == self.date.month and current_date.year == self.date.year:
            URL = CURRENT_MONTH_TREASURY_URL_TEMPLATE.format(
                year=self.date.year,
                month=f'{self.date.month:02}')
        else:
            URL = ANNUAL_TREASURY_URL_TEMPLATE.format(
                year=self.date.year)

        resp = requests.get(URL, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()

        data = StringIO(resp.content.decode('utf-8'))
        dict_reader = csv.DictReader(data)

        for row in dict_reader:
            data_date = parse(row.pop('Date'))

            if data_date.date() == self.date:
                for key, val in row.items():
                    setattr(self, self._treasury_map[key], val)
                break
        else:
            logger.warning(f'Treasury data for {self.date} was not found')

    def save(self, *args, **kwargs):
        self._retrieve_treasury_data()
        super().save(*args, **kwargs)

    def _par_rates(self):
        return [
            getattr(self, attr)
            for attr in self._maturity_order]

    def _zero_rates(self):
        zero_rates = []

        for idx, attr in enumerate(self._maturity_order):
            par_rate = getattr(self, attr)

            if idx == 0:
                zero_rates.append(par_rate)
                continue

            discounts_sum = 0
            for i in range(idx):
                discounts_sum += (par_rate / 2) / (1 + zero_rates[i] / 2) ** (i + 1)

            remainder = 100 - discounts_sum
            zero_rate = (((100 + par_rate / 2) / remainder) ** (1 / (i + 1)) - 1) * 2
            zero_rates.append(zero_rate * 100)
        return zero_rates
