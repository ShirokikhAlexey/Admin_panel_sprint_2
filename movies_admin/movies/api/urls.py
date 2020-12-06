from django.urls import path
from django.urls import include

urlpatterns = [
    path('v1/', include('movies.api.v1.urls'))
]