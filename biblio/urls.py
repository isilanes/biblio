# Django libs:
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

# Our libs:
from DjangoProgress import settings


# URL patterns:
urlpatterns = [
    # Admin view:
    path('admin/', admin.site.urls),

    # Main:
    path('', TemplateView.as_view(template_name="main_index.html"), name="main_index"),
]

# Apps:
for app in settings.EXTRA_APPS:
    urlpatterns.append(path(f'{app}/', include(f'{app}.urls', namespace=app)))
