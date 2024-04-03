from django.contrib import admin

from rates.models import TreasuryData

# Register your models here.
@admin.register(TreasuryData)
class DataSetAdmin(admin.ModelAdmin):
    ordering = ('-date',)
    readonly_fields = (
        'one_month',
        'two_month',
        'three_month',
        'four_month',
        'six_month',
        'one_year',
        'two_year',
        'three_year',
        'five_year',
        'seven_year',
        'ten_year',
        'twenty_year',
        'thirty_year',
    )
