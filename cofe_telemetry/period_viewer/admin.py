from django.contrib import admin

from .models import Shop, Shift, Telemetry, Premisions


class ShopAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address')
    search_fields = ('id', 'name', 'address')
    list_editable = ['name']

class PremAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'shops')
    search_fields = ('id', 'user', 'shops')
    list_editable = ['shops']

class ShiftAdmin(admin.ModelAdmin):
    list_display = ('videos', 'motion', 'createdAt', 'updatedAt', 'shop')
    list_display_links = ('videos', 'motion', 'createdAt', 'updatedAt', 'shop')
    search_fields = ('videos', 'motion', 'createdAt', 'updatedAt', 'shop')



admin.site.register(Shop, ShopAdmin)
admin.site.register(Shift, ShiftAdmin)
admin.site.register(Telemetry)
admin.site.register(Premisions)