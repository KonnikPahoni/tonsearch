from django.contrib import admin, messages

from tonnftscan.models import Collection


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "created_at",
    )
    list_per_page = 15

    search_fields = ["name"]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return qs.order_by("-created_at")
