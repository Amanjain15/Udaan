from django.contrib import admin

# Register your models here.
from theatre.models import *

class ScreenDataAdmin(admin.ModelAdmin):
    list_display = ["id","name","row_num"]
    search_fields=["name"]

admin.site.register(ScreenData, ScreenDataAdmin)

class RowDataAdmin(admin.ModelAdmin):
    list_display = ["id","name","seat_num","screen"]
    search_fields=["name"]

admin.site.register(RowData, RowDataAdmin)

class SeatDataAdmin(admin.ModelAdmin):
    list_display = ["id","seat_no","aisle_seat","row","reserved"]
    search_fields=["seat_no"]

admin.site.register(SeatData, SeatDataAdmin)

class ReservationDataAdmin(admin.ModelAdmin):
    list_display = ["transaction_id","seat_data","timestamp"]
    search_fields=["transaction_id"]

admin.site.register(ReservationData, ReservationDataAdmin)