from django.contrib import admin

from .models import PredictionLog


@admin.register(PredictionLog)
class PredictionLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "locality",
        "total_sqft",
        "bhk",
        "bathrooms",
        "furnishing",
        "predicted_price",
        "model_used",
        "created_at",
    )
    list_filter = ("furnishing", "model_used", "created_at")
    search_fields = ("locality",)
    readonly_fields = (
        "locality",
        "total_sqft",
        "bhk",
        "bathrooms",
        "furnishing",
        "property_age",
        "parking",
        "clubhouse",
        "metro_distance_km",
        "predicted_price",
        "price_per_sqft",
        "range_low",
        "range_high",
        "model_used",
        "report",
        "emailed_to",
        "created_at",
    )
