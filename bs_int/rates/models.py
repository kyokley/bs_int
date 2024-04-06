import csv
import requests
import logging

from io import BytesIO
from pathlib import Path

from collections import namedtuple

from io import StringIO
from dateutil.parser import parse
from openpyxl import load_workbook

from django.db import models
from django.utils import timezone

REQUEST_TIMEOUT = 60

CURRENT_MONTH_TREASURY_URL_TEMPLATE = 'https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/all/{year}{month}?type=daily_treasury_yield_curve&field_tdr_date_value_month={year}{month}&page&_format=csv'

ANNUAL_TREASURY_URL_TEMPLATE = 'https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{year}/all?type=daily_treasury_yield_curve&field_tdr_date_value={year}&page&_format=csv'

logger = logging.getLogger(__file__)

EXCEL_TEMPLATE_FILE = Path(__file__).parent / 'quant_assessment_template.xlsx'
PAR_VALUES_COL = 'C'
PAR_VALUES_START_ROW = 19
ZERO_RATES_COL = 'D'
ZERO_RATES_START_ROW = 19

Maturity = namedtuple('Maturity', 'name,months')

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

    _maturity_order = (
        Maturity(name='six_month', months=6),
        Maturity(name='one_year', months=12),
        Maturity(name='two_year', months=24),
        Maturity(name='three_year', months=36),
        Maturity(name='five_year', months=60),
        Maturity(name='seven_year', months=84),
        Maturity(name='ten_year', months=120),
        Maturity(name='twenty_year', months=240),
        Maturity(name='thirty_year', months=360),
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

    @classmethod
    def _effective_maturities(cls, maturity):
        for m in cls._maturity_order:
            if m.months < maturity.months:
                yield m

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
            getattr(self, maturity.name)
            for maturity in self._maturity_order]

    def _zero_rates(self):
        zero_rates = {}

        for idx, maturity in enumerate(self._maturity_order):
            logger.debug(f'Calculating {maturity.name}...')

            par_rate = getattr(self, maturity.name) / 100

            if idx == 0:
                zero_rates[maturity] = ((1 + par_rate / 2) ** (1 / maturity.months) - 1)
                # zero_rates[maturity] = par_rate * 100
                continue

            discounts_sum = 0
            months = 0
            for m in self._effective_maturities(maturity):
                while months < m.months:
                    months += 6
                    discounts = (par_rate / 2) / (1 + zero_rates[m]) ** months
                    discounts_sum += discounts

            remainder = 1 - discounts_sum
            zero_rate = (((1 + par_rate / 2) / remainder) ** (1 / maturity.months) - 1)
            zero_rates[maturity] = zero_rate

        logger.debug(zero_rates)
        return zero_rates

    def to_excel(self):
        excel = Excel()
        excel.populate_data(self._par_rates(),
                            self._zero_rates())
        return excel.stream()


class Excel:
    def __init__(self):
        self.wb = load_workbook(filename=EXCEL_TEMPLATE_FILE)

    def populate_data(self, par_values, zero_rates):
        ws = self.wb.active

        for idx, par_val in enumerate(par_values, start=PAR_VALUES_START_ROW):
            ws[f'{PAR_VALUES_COL}{idx}'] = par_val

        for idx, zero_rate in enumerate(zero_rates, start=ZERO_RATES_START_ROW):
            ws[f'{ZERO_RATES_COL}{idx}'] = zero_rate

    def stream(self):
        output = BytesIO()
        self.wb.save(output)
        output.seek(0)
        return output
