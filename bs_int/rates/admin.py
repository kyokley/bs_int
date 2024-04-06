from django.contrib import admin

from rates.models import TreasuryData, Excel
from django.http import HttpResponse

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
    actions = ('download_excel',)

    def download_excel(self, request, queryset):
        excel = Excel()

        tdatas = list(queryset.order_by('date'))
        for tdata in tdatas:
            excel.add_sheet(tdata)

        output = excel.stream()

        if len(tdatas) == 1:
            filename = f'curve_{tdata.date.year}-{tdata.date.month}-{tdata.date.day}'
        else:
            filename = (
                f'curve_{tdatas[0].date.year}.{tdatas[0].date.month}.{tdatas[0].date.day}'
                f'-{tdatas[-1].date.year}.{tdatas[-1].date.month}.{tdatas[-1].date.day}'
            )

        response = HttpResponse(content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = f"attachment; filename={filename}.xlsx"
        response.write(output.getvalue())
        return response
