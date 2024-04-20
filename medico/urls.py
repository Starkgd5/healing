from django.urls import path
from medico.views import cadastro_medico, abrir_horario, consultas_medico


urlpatterns = [
    path('cadastro_medico/', cadastro_medico, name="cadastro_medico"),
    path('abrir_horario/', abrir_horario, name="abrir_horario"),
    path('consultas_medico/', consultas_medico, name="consultas_medico"),
]
