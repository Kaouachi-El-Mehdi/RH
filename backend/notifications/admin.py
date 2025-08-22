from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
	list_display = ('title', 'recipient', 'created_at', 'is_read')
	search_fields = ('title', 'message', 'recipient__username')
