
from django.urls import path, include
from login.views import test, handle_redirect, send_code


urlpatterns = [
    path(r'login/', test),
    path(r'second_authen/', handle_redirect),

]