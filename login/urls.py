
from django.urls import path, include
from login.views import test, handle_redirect, send_req_to_gw, redirect_to_login, cert_upload


urlpatterns = [
    path(r'', redirect_to_login),
    path(r'login/', test),
    path(r'send_request/', send_req_to_gw),
    path(r'second_authen/', handle_redirect),
    path(r'cert_upload/', cert_upload),

]