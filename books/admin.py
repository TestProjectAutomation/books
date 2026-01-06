from django.contrib import admin

# Register your models here.

from .models import Book
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author_name", "is_published", "uploaded_by", "created_at")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "author_name", "description")
    list_filter = ("is_published", "created_at", "uploaded_by")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
    fieldsets = (
        (None, {
            "fields": ("title", "slug", "author_name", "description", "cover", "pdf_file", "content", "is_published", "uploaded_by")
        }),
        ("Timestamps", {
            "fields": ("created_at",),
        }),
    )
    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
