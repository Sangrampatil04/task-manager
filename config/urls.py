from django.contrib import admin
from django.urls import path, include
from tasks.views import home

urlpatterns = [
    path('admin/', admin.site.urls),

    # Home redirects to dashboard
    path('', home, name='home'),

    # All task app URLs
    path('', include('tasks.urls')),
]
