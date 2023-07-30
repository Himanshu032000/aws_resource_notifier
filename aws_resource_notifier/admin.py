from django.contrib import admin, messages
from aws_resource_notifier.models.subscription import Subscription


class SubscriptionAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return [field.name for field in self.model._meta.fields]
        return []
    
    def has_change_permission(self, request, obj=None):
        return not obj

    def response_change(self, request, obj):
        if "_save" in request.POST:
            message = "Updates to Subscription objects are not allowed. Only delete is permitted."
            self.message_user(request, message, level=messages.ERROR)

        return super().response_change(request, obj)

admin.site.register(Subscription, SubscriptionAdmin)
