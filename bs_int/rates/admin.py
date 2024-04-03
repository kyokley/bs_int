from django.contrib import admin

from bs_int.rates.models import DataSet

# Register your models here.
@admin.register(DataSet)
class DataSetAdmin(admin.ModelAdmin):
    ordering = ('-date',)
