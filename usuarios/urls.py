from django.urls import path

from usuarios.views import (cadastro, cadastro_profile, escolher_tipo,
                            login_view, sair)

urlpatterns = [
    path("cadastro/", cadastro, name="cadastro"),
    path('login/', login_view, name="login"),
    path('sair/', sair, name="sair"),
    path('cadastro_profile/', cadastro_profile, name="cadastro_profile"),
    path('escolher_tipo/', escolher_tipo, name="escolher_tipo"),
]
