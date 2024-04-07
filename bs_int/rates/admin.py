import zipfile
from io import BytesIO

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
    actions = ('download_excel',
               'download_csv',
               )

    def download_csv(self, request, queryset):
        tdatas = list(queryset.order_by('date'))

        if len(tdatas) == 1:
            filename = (
                f'curve_{tdatas[0].date.year}-{tdatas[0].date.month}-{tdatas[0].date.day}'
            )

            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = f"attachment; filename={filename}.csv"
            response.write(tdatas[0].to_csv().read())
        else:
            io = BytesIO()

            with zipfile.ZipFile(io, 'w') as zf:
                for tdata in tdatas:
                    filename = self._filename(tdata)
                    zf.writestr(f'{filename}.csv',
                                tdata.to_csv().read())

            zip_filename = self._filename(tdatas)

            response = HttpResponse(content_type="application/x-zip-compressed")
            response.write(io.getvalue())
            response['Content-Disposition'] = f'attachment; filename={zip_filename}.zip'
        return response

    @staticmethod
    def _filename(tdatas):
        try:
            if len(tdatas) == 1:
                filename = (
                    f'curve_{tdatas[0].date.year}-{tdatas[0].date.month}-{tdatas[0].date.day}'
                )
            else:
                filename = (
                    f'curve_{tdatas[0].date.year}.{tdatas[0].date.month}.{tdatas[0].date.day}'
                    f'-{tdatas[-1].date.year}.{tdatas[-1].date.month}.{tdatas[-1].date.day}'
                )
        except Exception:
            filename = (
                f'curve_{tdatas.date.year}-{tdatas.date.month}-{tdatas.date.day}'
            )

        return filename

    def download_excel(self, request, queryset):
        excel = Excel()

        tdatas = list(queryset.order_by('date'))
        for tdata in tdatas:
            excel.add_sheet(tdata)

        output = excel.stream()

        filename = self._filename(tdatas)

        response = HttpResponse(content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = f"attachment; filename={filename}.xlsx"
        response.write(output.getvalue())
        return response
