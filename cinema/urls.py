"""cinema URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path, include, reverse, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from movies import views
from user.views import UserViewSet, ObtainTokenView


router = routers.DefaultRouter()
router.register(r'films', views.FilmViewSet)
router.register(r'halls', views.HallVieSet)
router.register(r'seances', views.SeanceViewSet)
router.register(r'tickets', views.TicketViewSet)
router.register(r'user', UserViewSet)


urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.index, name='homepage'),
    path('admin/', admin.site.urls),
    path('obtain_token/', ObtainTokenView.as_view()),
    path('movies/', include('movies.urls')),
    path('user/', include('user.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



