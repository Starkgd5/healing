from django.urls import path
from usuarios.views import cadastro, login_view, sair

urlpatterns = [
    path("cadastro/", cadastro, name="cadastro"),
    path('login/', login_view, name="login"),
    path('sair/', sair, name="sair")
]
