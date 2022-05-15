from django.contrib import admin

from .models import Shop, Shift, Telemetry


class ShopAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('id', 'name')
    list_editable = ['name']

class ShiftAdmin(admin.ModelAdmin):
    list_display = ('videos', 'motion', 'createdAt', 'updatedAt', 'shop')
    list_display_links = ('videos', 'motion', 'createdAt', 'updatedAt', 'shop')
    search_fields = ('videos', 'motion', 'createdAt', 'updatedAt', 'shop')


class TelemetryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('id', 'name')
    # list_editable = ('name',)


admin.site.register(Shop, ShopAdmin)
admin.site.register(Shift, ShiftAdmin)
admin.site.register(Telemetry)