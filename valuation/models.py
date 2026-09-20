from django.db import models


class PredictionLog(models.Model):
    """Every valuation computed by the ML pipeline."""

    class Furnishing(models.TextChoices):
        UNFURNISHED = "unfurnished", "Unfurnished"
        SEMI_FURNISHED = "semi_furnished", "Semi-Furnished"
        FULLY_FURNISHED = "fully_furnished", "Fully-Furnished"

    locality = models.CharField(max_length=120, db_index=True)
    total_sqft = models.FloatField()
    bhk = models.PositiveSmallIntegerField()
    bathrooms = models.PositiveSmallIntegerField()
    furnishing = models.CharField(max_length=20, choices=Furnishing.choices)
    property_age = models.FloatField(default=0)
    parking = models.BooleanField(default=False)
    clubhouse = models.BooleanField(default=False)
    metro_distance_km = models.FloatField(null=True, blank=True)

    predicted_price = models.DecimalField(max_digits=14, decimal_places=2)
    price_per_sqft = models.DecimalField(max_digits=12, decimal_places=2)
    range_low = models.DecimalField(max_digits=14, decimal_places=2)
    range_high = models.DecimalField(max_digits=14, decimal_places=2)
    model_used = models.CharField(max_length=30, default="xgboost")

    report = models.FileField(upload_to="reports/", null=True, blank=True)
    emailed_to = models.EmailField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Prediction log"
        verbose_name_plural = "Prediction logs"

    def __str__(self) -> str:
        return f"#{self.pk} {self.locality} — ₹{self.predicted_price:,.0f}"
