from django.contrib import admin
from paciente.models import Consulta

# Register your models here.
@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'data_aberta', 'status']
