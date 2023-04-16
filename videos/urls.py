from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin-panel/', admin.site.urls),
    path('api/video/', include('videoslist_app.api.urls')),
    path('api/account/', include('user_app.api.urls')),

]