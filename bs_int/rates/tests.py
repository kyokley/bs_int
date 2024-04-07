from datetime import date
import pytest

from rates.models import Maturity, TreasuryData


MOCK_DATA = 'Date,"1 Mo","2 Mo","3 Mo","4 Mo","6 Mo","1 Yr","2 Yr","3 Yr","5 Yr","7 Yr","10 Yr","20 Yr","30 Yr"\n04/05/2024,5.47,5.50,5.43,5.41,5.34,5.05,4.73,4.54,4.38,4.39,4.39,4.65,4.54\n04/04/2024,5.47,5.49,5.41,5.40,5.32,5.00,4.65,4.46,4.30,4.31,4.31,4.57,4.47\n04/03/2024,5.47,5.44,5.42,5.40,5.33,5.03,4.68,4.48,4.34,4.36,4.36,4.61,4.51\n04/02/2024,5.49,5.45,5.42,5.40,5.34,5.05,4.70,4.51,4.35,4.37,4.36,4.61,4.51\n04/01/2024,5.49,5.47,5.44,5.41,5.36,5.06,4.72,4.51,4.34,4.33,4.33,4.58,4.47'


class TestEffectiveMaturities:
    @pytest.mark.parametrize(
        'test_maturity_months,expected',
        (
            (12, []),
            (
                18,
                [
                    Maturity(name='one_year', months=12),
                ]
            ),
            (
                40,
                [
                    Maturity(name='one_year', months=12),
                    Maturity(name='two_year', months=24),
                    Maturity(name='three_year', months=36),
                ]
            ),
        )
    )
    def test_maturities(self,
                        test_maturity_months,
                        expected):
        assert list(
            TreasuryData._effective_maturities(
            Maturity(months=test_maturity_months,
                     name='test_maturity')
        )) == expected


@pytest.mark.django_db
class TestRetrieveTreasuryData:
    @pytest.fixture(autouse=True)
    def setUp(self, mocker):
        self.mock_get = mocker.patch(
            'rates.models.requests.get')

        self.mock_get.return_value.content.decode.return_value = MOCK_DATA
        self.treasury_data = TreasuryData(
            date=date(2024, 4, 1))

    def test_retrieve(self):
        self.treasury_data._retrieve_treasury_data()
        self.treasury_data.save()

        self.treasury_data.refresh_from_db()

        assert self.treasury_data.one_month == 5.49
        assert self.treasury_data.two_month == 5.47
        assert self.treasury_data.three_month == 5.44
        assert self.treasury_data.four_month == 5.41
        assert self.treasury_data.six_month == 5.36
        assert self.treasury_data.one_year == 5.06
        assert self.treasury_data.two_year == 4.72
        assert self.treasury_data.three_year == 4.51
        assert self.treasury_data.five_year == 4.34
        assert self.treasury_data.seven_year == 4.33
        assert self.treasury_data.ten_year == 4.33
        assert self.treasury_data.twenty_year == 4.58
        assert self.treasury_data.thirty_year == 4.47
