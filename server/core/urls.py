from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('telegram/', include('account.urls')),  # Replace with the name of your app
]
