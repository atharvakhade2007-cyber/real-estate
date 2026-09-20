from rest_framework import serializers

from .models import PredictionLog


class PropertyInputSerializer(serializers.Serializer):
    """Validates the property valuation payload sent by the dashboard."""

    locality = serializers.CharField(max_length=120)
    total_sqft = serializers.FloatField(min_value=300, max_value=10000)
    bhk = serializers.IntegerField(min_value=1, max_value=5)
    bathrooms = serializers.IntegerField(min_value=1, max_value=5)
    furnishing = serializers.ChoiceField(choices=PredictionLog.Furnishing.choices)
    property_age = serializers.FloatField(min_value=0, max_value=50, required=False, default=0)
    parking = serializers.BooleanField(required=False, default=False)
    clubhouse = serializers.BooleanField(required=False, default=False)
    metro_distance_km = serializers.FloatField(min_value=0, max_value=25, required=False, allow_null=True, default=None)

    def validate_locality(self, value: str) -> str:
        return value.strip()


class EmailReportSerializer(serializers.Serializer):
    prediction_id = serializers.IntegerField(min_value=1)
    email = serializers.EmailField()


class GeneratePdfSerializer(serializers.Serializer):
    prediction_id = serializers.IntegerField(min_value=1)


class PredictionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictionLog
        fields = [
            "id",
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
        ]
