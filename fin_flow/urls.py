from django.contrib import admin
from django.urls import path, include

url_version = "api/v1"


urlpatterns = [
    path("admin/", admin.site.urls),
    path(f"{url_version}/auth/", include("user_authentication.urls")),
    path(f"{url_version}/transactions/", include("transactions.urls")),
    # path("api/", include("admin_controls.urls")),
]
