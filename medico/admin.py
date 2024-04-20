from django.contrib import admin

from .models import DadosMedico, DatasAbertas, Especialidades


@admin.register(Especialidades)
class EspecialidadesAdmin(admin.ModelAdmin):
    list_display = ['especialidade', 'icone']


@admin.register(DadosMedico)
class DadosMedicoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'especialidade', 'foto', 'user']


@admin.register(DatasAbertas)
class DatasAbertasAdmin(admin.ModelAdmin):
    list_display = ['data', 'user', 'agendado']
