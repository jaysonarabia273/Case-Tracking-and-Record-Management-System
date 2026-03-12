from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
    path('', include('django.contrib.auth.urls')),
    path('auth/', include('social_django.urls', namespace='social')),
]

# Django Debug Toolbar
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


def permission_denied_view(request, exception):
    return HttpResponse("Access denied: Only @cvsu.edu.ph emails allowed.", status=403)

handler403 = permission_denied_view