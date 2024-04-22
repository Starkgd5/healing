from django.urls import path

from paciente.views import (agendar_horario, cancelar_consulta,
                            consulta_paciente, escolher_horario, home,
                            minhas_consultas)

urlpatterns = [
    path('home/', home, name="home"),
    path('escolher_horario/<int:id_dados_medicos>/',
         escolher_horario, name="escolher_horario"),
    path('agendar_horario/<int:id_data_aberta>/',
         agendar_horario, name="agendar_horario"),
    path('minhas_consultas/', minhas_consultas, name="minhas_consultas"),
    path('consulta/<int:id_consulta>/', consulta_paciente, name="consulta"),
    path('cancelar_consulta/<int:id_consulta>/',
         cancelar_consulta, name="cancelar_consulta")
]
