from django.urls import path

from usuarios.views import (cadastro, cadastro_profile, editar_perfil,
                            escolher_tipo, excluir_perfil, login_view,
                            perfil_list, sair, selecionar_perfil)

urlpatterns = [
    path("cadastro/", cadastro, name="cadastro"),
    path('login/', login_view, name="login"),
    path('sair/', sair, name="sair"),
    path('cadastro_profile/', cadastro_profile, name="cadastro_profile"),
    path('escolher_tipo/', escolher_tipo, name="escolher_tipo"),
    path('selecionar_perfil/', selecionar_perfil, name="selecionar_perfil"),
    path('perfil_list/', perfil_list, name="perfil_list"),
    path('editar_perfil/<int:profile_id>/',
         editar_perfil, name="editar_perfil"),
    path('excluir_perfil/<int:profile_id>/',
         excluir_perfil, name="excluir_perfil"),
]
