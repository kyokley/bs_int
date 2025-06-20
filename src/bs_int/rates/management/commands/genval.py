import logging

from django.core.management.base import BaseCommand
from rates.models import TreasuryData

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = "Initialize Data"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **kwargs):
        first = TreasuryData.objects.first()
        first._zero_rates()
