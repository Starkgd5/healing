from django.contrib import admin

from .models import DadosMedico, DatasAbertas, Especialidades


@admin.register(Especialidades)
class EspecialidadesAdmin(admin.ModelAdmin):
    list_display = ['especialidade', 'icone']


@admin.register(DadosMedico)
class DadosMedicoAdmin(admin.ModelAdmin):
    list_display = ['especialidade', 'profile']


@admin.register(DatasAbertas)
class DatasAbertasAdmin(admin.ModelAdmin):
    list_display = ['data', 'profile', 'agendado']
