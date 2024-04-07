import pytest

from rates.models import Maturity, TreasuryData


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
