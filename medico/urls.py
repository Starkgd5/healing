from django.urls import path

from medico.views import (abrir_horario, add_documento, cadastro_medico,
                          consulta_area_medico, consultas_medico,
                          finalizar_consulta)

urlpatterns = [
    path('cadastro_medico/', cadastro_medico, name="cadastro_medico"),
    path('abrir_horario/', abrir_horario, name="abrir_horario"),
    path('consultas_medico/', consultas_medico, name="consultas_medico"),
    path('consulta_area_medico/<int:id_consulta>/',
         consulta_area_medico, name="consulta_area_medico"),
    path('finalizar_consulta/<int:id_consulta>/',
         finalizar_consulta, name="finalizar_consulta"),
    path('add_documento/<int:id_consulta>/',
         add_documento, name="add_documento"),
]
