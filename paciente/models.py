from datetime import date

from django.contrib.auth.models import User
from django.db import models

from medico.models import DatasAbertas
from usuarios.models import UserProfile


class Consulta(models.Model):
    status_choices = (
        ('A', 'Agendada'),
        ('F', 'Finalizada'),
        ('C', 'Cancelada'),
        ('I', 'Iniciada')

    )
    paciente = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    data_aberta = models.ForeignKey(DatasAbertas, on_delete=models.DO_NOTHING)
    status = models.CharField(
        max_length=1, choices=status_choices, default='A')
    link = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.paciente.username


class DadosPaciente(models.Model):
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
    cns = models.CharField(max_length=25, unique=True, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    mother_name = models.CharField(max_length=255, null=True, blank=True)
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def age(self):
        if self.birth_date:
            today = date.today()
            age = today.year - self.birth_date.year - \
                ((today.month, today.day) <
                 (self.birth_date.month, self.birth_date.day))
            return age
        else:
            return None

    def __str__(self):
        return self.profile.nome
