import logging
import os

from django.conf import settings
from django.http import FileResponse, Http404, JsonResponse
from django.views.static import serve as static_serve
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .ml import price_model
from .models import PredictionLog
from .reports import ensure_report_file, send_report_email
from .serializers import (
    EmailReportSerializer,
    GeneratePdfSerializer,
    PredictionLogSerializer,
    PropertyInputSerializer,
)

logger = logging.getLogger(__name__)


class PredictView(APIView):
    """POST /api/predict/ — validate input, run the ML pipeline, log & return."""

    throttle_scope = "predict"

    def post(self, request):
        serializer = PropertyInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        try:
            result = price_model.predict(payload)
        except (ValueError, RuntimeError) as exc:
            logger.error("Prediction failed: %s", exc)
            return Response(
                {"detail": str(exc), "code": "model_error"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        log = PredictionLog.objects.create(
            locality=result["locality"],
            total_sqft=payload["total_sqft"],
            bhk=payload["bhk"],
            bathrooms=payload["bathrooms"],
            furnishing=payload["furnishing"],
            property_age=payload["property_age"],
            parking=payload["parking"],
            clubhouse=payload["clubhouse"],
            metro_distance_km=payload["metro_distance_km"],
            predicted_price=result["estimated_price"],
            price_per_sqft=result["price_per_sqft"],
            range_low=result["range_low"],
            range_high=result["range_high"],
            model_used=result["model_used"],
        )

        return Response(
            {
                "id": log.id,
                "estimated_price": result["estimated_price"],
                "price_per_sqft": result["price_per_sqft"],
                "range_low": result["range_low"],
                "range_high": result["range_high"],
                "model_used": result["model_used"],
                "currency": "INR",
                "created_at": log.created_at,
            },
            status=status.HTTP_201_CREATED,
        )


class LocalitiesView(APIView):
    """GET /api/localities/ — feeds the searchable locality dropdown."""

    def get(self, request):
        return Response({"localities": price_model.localities()})


class PredictionListView(APIView):
    """GET /api/predictions/ — recent valuations (Saved Valuations tab)."""

    def get(self, request):
        logs = PredictionLog.objects.all()[:100]
        return Response(PredictionLogSerializer(logs, many=True).data)


class GeneratePdfView(APIView):
    """POST /api/generate-pdf/ — builds the ReportLab PDF synchronously."""

    throttle_scope = "reports"

    def post(self, request):
        serializer = GeneratePdfSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        prediction_id = serializer.validated_data["prediction_id"]

        try:
            log = PredictionLog.objects.get(pk=prediction_id)
        except PredictionLog.DoesNotExist:
            return Response(
                {"detail": f"Prediction {prediction_id} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            ensure_report_file(log)
        except Exception as exc:  # noqa: BLE001
            logger.exception("PDF generation failed for prediction %s", prediction_id)
            return Response(
                {"detail": f"PDF generation failed: {exc}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(
            {
                "prediction_id": prediction_id,
                "download_url": f"/api/reports/{prediction_id}/download/",
                "file_size": log.report.size,
            },
            status=status.HTTP_200_OK,
        )


class EmailReportView(APIView):
    """POST /api/email-report/ — builds the PDF and emails it synchronously."""

    throttle_scope = "reports"

    def post(self, request):
        serializer = EmailReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        prediction_id = serializer.validated_data["prediction_id"]
        email = serializer.validated_data["email"]

        try:
            log = PredictionLog.objects.get(pk=prediction_id)
        except PredictionLog.DoesNotExist:
            return Response(
                {"detail": f"Prediction {prediction_id} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            send_report_email(log, email)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Email delivery failed for prediction %s", prediction_id)
            return Response(
                {"detail": f"Email delivery failed: {exc}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(
            {
                "prediction_id": prediction_id,
                "emailed_to": email,
                "download_url": f"/api/reports/{prediction_id}/download/",
            },
            status=status.HTTP_200_OK,
        )


class ReportDownloadView(APIView):
    """GET /api/reports/<id>/download/ — stream the generated PDF."""

    def get(self, request, prediction_id: int):
        try:
            log = PredictionLog.objects.get(pk=prediction_id)
        except PredictionLog.DoesNotExist:
            return Response(
                {"detail": "Report not found."}, status=status.HTTP_404_NOT_FOUND
            )
        if not log.report:
            return Response(
                {"detail": "PDF has not been generated yet."},
                status=status.HTTP_404_NOT_FOUND,
            )
        response = FileResponse(log.report.open("rb"), content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="propval-valuation-{prediction_id}.pdf"'
        )
        return response


def spa(request, path=""):
    """Serves the built React SPA (frontend/dist) with index.html fallback.

    Non-API GETs hit this view; unknown client-side routes fall back to
    index.html so React Router-style navigation keeps working.
    """
    dist = settings.FRONTEND_DIST_DIR
    if not settings.SERVE_FRONTEND or not dist.exists():
        raise Http404("Frontend build not found — run `npm run build` in frontend/.")

    if path:
        candidate = (dist / path).resolve()
        # Prevent path traversal outside dist/.
        if candidate.is_file() and str(candidate).startswith(str(dist.resolve())):
            return FileResponse(candidate.open("rb"))

    index = dist / "index.html"
    if not index.exists():
        raise Http404("Frontend build not found — run `npm run build` in frontend/.")
    return FileResponse(index.open("rb"))
