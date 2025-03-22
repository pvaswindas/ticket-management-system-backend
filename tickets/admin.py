from django.contrib import admin
from .models import Ticket


class TicketAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'priority',
        'status',
        'created_user',
        'assigned_to',
        'created_at'
    )
    list_filter = ('priority', 'status')
    search_fields = (
        'title', 'description', 'created_user__username', 'assigned_to'
    )


admin.site.register(Ticket, TicketAdmin)
