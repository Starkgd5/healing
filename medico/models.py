from datetime import datetime

from django.db import models

from usuarios.models import UserProfile


def is_medico(profile):
    return DadosMedico.objects.filter(profile=profile).exists()


class Especialidades(models.Model):
    especialidade = models.CharField(max_length=100)
    icone = models.ImageField(upload_to="icones", null=True, blank=True)

    def __str__(self):
        return self.especialidade


class DadosMedico(models.Model):
    crm = models.CharField(max_length=30)
    cedula_identidade_medica = models.ImageField(upload_to='cim')
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    descricao = models.TextField(null=True, blank=True)
    especialidade = models.ForeignKey(
        Especialidades, on_delete=models.DO_NOTHING, null=True, blank=True)
    valor_consulta = models.FloatField(default=100)

    def __str__(self):
        return self.profile.nome

    @property
    def proxima_data(self):
        proxima_data = DatasAbertas.objects.filter(
            profile=self.profile).filter(
                data__gt=datetime.now()).filter(
                    agendado=False).order_by('data').first()
        return proxima_data


class DatasAbertas(models.Model):
    data = models.DateTimeField()
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    agendado = models.BooleanField(default=False)

    def __str__(self) -> str:
        return str(self.data)


class Documento(models.Model):
    consulta = models.ForeignKey(
        'paciente.Consulta',  on_delete=models.DO_NOTHING)
    titulo = models.CharField(max_length=30)
    documento = models.FileField(upload_to='documentos')

    def __str__(self) -> str:
        return self.titulo
