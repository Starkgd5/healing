from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages import constants
from django.shortcuts import redirect, render

from medico.models import DadosMedico, DatasAbertas, Especialidades, is_medico
from paciente.models import Consulta


@login_required
def home(request):
    if request.method == "GET":
        medicos = DadosMedico.objects.all()
        especialidades = Especialidades.objects.all()

        medico_filtrar = request.GET.get('medico')
        especialidades_filtrar = request.GET.getlist('especialidades')

        if medico_filtrar:
            medicos = medicos.filter(nome__icontains=medico_filtrar)

        if especialidades_filtrar:
            medicos = medicos.filter(
                especialidade_id__in=especialidades_filtrar)

        context = {
            'medicos': medicos,
            'especialidades': especialidades,
            'is_medico': is_medico(request.user)
        }
        return render(request, 'home.html', context)


@login_required
def escolher_horario(request, id_dados_medicos):
    if request.method == "GET":
        medico = DadosMedico.objects.get(id=id_dados_medicos)
        datas_abertas = DatasAbertas.objects.filter(user=medico.user).filter(
            data__gte=datetime.now()).filter(agendado=False)
        context = {
            'medico': medico,
            'datas_abertas': datas_abertas,
            'is_medico': is_medico(request.user)
        }
        return render(request, 'escolher_horario.html', context)


@login_required
def agendar_horario(request, id_data_aberta):
    if request.method == "GET":
        data_aberta = DatasAbertas.objects.get(id=id_data_aberta)

        horario_agendado = Consulta(
            paciente=request.user,
            data_aberta=data_aberta
        )

        horario_agendado.save()

        # TODO: Sugestão Tornar atomico

        data_aberta.agendado = True
        data_aberta.save()

        messages.add_message(request, constants.SUCCESS,
                             'Horário agendado com sucesso.')

        return redirect('/pacientes/minhas_consultas/')


@login_required
def minhas_consultas(request):
    if request.method == "GET":
        # TODO: desenvolver filtros
        historico_consultas = Consulta.objects.filter(
            paciente=request.user
        )
        minhas_consultas = Consulta.objects.filter(
            paciente=request.user).filter(
                data_aberta__data__gte=datetime.now())

        by_especialidades = request.GET.get('especialidades')
        by_data = request.GET.get('data')

        if by_data:
            minhas_consultas = minhas_consultas.filter(
                data_aberta__data__icontains=by_data)

        if by_especialidades:
            minhas_consultas = minhas_consultas.filter(
                data_aberta__user__medico_user__especialidade__especialidade__icontains=by_especialidades)

        context = {
            'minhas_consultas': minhas_consultas,
            'is_medico': is_medico(request.user),
            'historico_consultas': historico_consultas
        }
        return render(request, 'minhas_consultas.html', context)


def consulta(request, id_consulta):
    if request.method == 'GET':
        consulta = Consulta.objects.get(id=id_consulta)
        dado_medico = DadosMedico.objects.get(user=consulta.data_aberta.user)
        return render(request, 'consulta.html', {'consulta': consulta, 'dado_medico': dado_medico, 'is_medico': is_medico(request.user)})
