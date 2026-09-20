"""Root URL configuration — API under /api/, SPA catch-all at /."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

from valuation.views import spa

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("valuation.urls")),
    # Single-server mode: Django serves the built React app + its static assets.
    re_path(r"^(?P<path>.*)$", spa),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
