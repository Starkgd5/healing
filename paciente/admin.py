from django.contrib import admin
from paciente.models import Consulta, DadosPaciente

# Register your models here.
@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'data_aberta', 'status']


@admin.register(DadosPaciente)
class DadosPacienteAdmin(admin.ModelAdmin):
    list_display = ['cpf', 'profile']
