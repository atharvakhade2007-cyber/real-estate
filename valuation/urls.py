from django.urls import path

from .views import (
    EmailReportView,
    GeneratePdfView,
    LocalitiesView,
    PredictView,
    PredictionListView,
    ReportDownloadView,
)

app_name = "valuation"

urlpatterns = [
    path("predict/", PredictView.as_view(), name="predict"),
    path("localities/", LocalitiesView.as_view(), name="localities"),
    path("predictions/", PredictionListView.as_view(), name="predictions"),
    path("generate-pdf/", GeneratePdfView.as_view(), name="generate-pdf"),
    path("email-report/", EmailReportView.as_view(), name="email-report"),
    path(
        "reports/<int:prediction_id>/download/",
        ReportDownloadView.as_view(),
        name="report-download",
    ),
]
