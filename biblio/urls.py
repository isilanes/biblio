from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from biblio import settings


urlpatterns = [
    # Admin view:
    path('admin/', admin.site.urls),

    # Main:
    path('', TemplateView.as_view(template_name="main_index.html"), name="main_index"),
]

# Apps:
for app in settings.EXTRA_APPS:
    app_name = app.split(".")[-1]  # if app = "apps.app_name", "fix" it
    urlpatterns.append(path(f'{app_name}/', include(f'{app}.urls', namespace=app_name)))
