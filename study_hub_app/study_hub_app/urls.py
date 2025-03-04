"""
URL configuration for study_hub_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework.schemas import get_schema_view
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('study_hub.urls')),
    path('apischema/', get_schema_view(
        title= 'StudyHub REST API',
        description = "API for interacting with Studyhub database",
        version = "1.0"
    ), name="openapi-schema"),
    path('swaggerdocs/', TemplateView.as_view(
        template_name='study_hub/swagger-docs.html',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='swagger-ui')
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
